#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sincronização de Processos com Legal AI
Sincronização bidirecional de processos entre Painel Jurídico e Legal AI
"""

from typing import List, Dict, Tuple
from datetime import datetime
import json


class ProcessSync:
    """
    Gerenciador de sincronização de processos com Legal AI
    
    Fornece sincronização bidirecional:
    - Upload de processos para Legal AI
    - Download de análises do Legal AI
    - Resolução de conflitos
    """
    
    def __init__(self, legal_ai_client):
        """
        Inicializa o sincronizador
        
        Args:
            legal_ai_client: Instância de LegalAIClient
        """
        self.client = legal_ai_client
        self.last_sync = None
        self.sync_errors = []
    
    def sync_processo_to_remote(self, processo: Dict) -> Tuple[bool, str]:
        """
        Sincroniza um processo para Legal AI
        
        Args:
            processo: Dicionário com dados do processo
        
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            if not self.client.test_connection():
                return False, "Conexão com Legal AI falhou"
            
            # Preparar dados
            payload = {
                'numero_processo': processo.get('numero_processo'),
                'vara': processo.get('vara'),
                'reclamante': processo.get('reclamante'),
                'reclamada': processo.get('reclamada'),
                'status': processo.get('status'),
                'tese_inicial': processo.get('tese_inicial'),
                'tese_defesa': processo.get('tese_defesa'),
                'resultado': processo.get('resultado'),
            }
            
            # Enviar para Legal AI
            response = self.client.create_lawsuit_remote(payload)
            
            if response and response.get('id'):
                self.last_sync = datetime.now()
                return True, f"Processo {processo.get('numero_processo')} sincronizado com sucesso"
            else:
                error = response.get('error', 'Erro desconhecido') if response else 'Sem resposta'
                return False, f"Erro ao sincronizar: {error}"
        
        except Exception as e:
            error_msg = f"Erro ao sincronizar processo: {str(e)}"
            self.sync_errors.append(error_msg)
            return False, error_msg
    
    def sync_processos_batch(self, processos: List[Dict]) -> Dict:
        """
        Sincroniza múltiplos processos em lote
        
        Args:
            processos: Lista de processos
        
        Returns:
            Dict com estatísticas da sincronização
        """
        stats = {
            'total': len(processos),
            'sucesso': 0,
            'erro': 0,
            'mensagens': []
        }
        
        for processo in processos:
            sucesso, msg = self.sync_processo_to_remote(processo)
            if sucesso:
                stats['sucesso'] += 1
            else:
                stats['erro'] += 1
            stats['mensagens'].append(msg)
        
        return stats
    
    def get_processo_analysis(self, numero_processo: str) -> Tuple[bool, Dict]:
        """
        Obtém análise de um processo do Legal AI
        
        Args:
            numero_processo: Número do processo
        
        Returns:
            Tuple[bool, Dict]: (sucesso, análise)
        """
        try:
            if not self.client.test_connection():
                return False, {'error': 'Conexão com Legal AI falhou'}
            
            # Buscar análise
            analysis = self.client.get_lawsuit_analysis(numero_processo)
            
            if analysis:
                return True, analysis
            else:
                return False, {'error': 'Análise não encontrada'}
        
        except Exception as e:
            error_msg = f"Erro ao obter análise: {str(e)}"
            self.sync_errors.append(error_msg)
            return False, {'error': error_msg}
    
    def resolve_conflict(self, local_data: Dict, remote_data: Dict, priority: str = 'local') -> Dict:
        """
        Resolve conflitos entre dados locais e remotos
        
        Args:
            local_data: Dados locais
            remote_data: Dados remotos
            priority: 'local' ou 'remote' (qual versão prevalece)
        
        Returns:
            Dict: Dados reconciliados
        """
        if priority == 'local':
            merged = local_data.copy()
            # Adicionar campos de análise do remote
            if remote_data.get('analysis'):
                merged['legal_ai_analysis'] = remote_data['analysis']
        else:  # priority == 'remote'
            merged = remote_data.copy()
            # Preservar campos críticos locais
            merged['id'] = local_data.get('id')
            merged['created_at'] = local_data.get('created_at')
        
        merged['last_sync'] = datetime.now().isoformat()
        merged['sync_status'] = 'synced'
        
        return merged
    
    def get_sync_status(self) -> Dict:
        """
        Retorna status da sincronização
        
        Returns:
            Dict com status
        """
        return {
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'connected': self.client.test_connection(),
            'errors': len(self.sync_errors),
            'recent_errors': self.sync_errors[-5:] if self.sync_errors else []
        }
    
    def export_for_sync(self, processos: List[Dict]) -> str:
        """
        Exporta processos em formato pronto para sincronização
        
        Args:
            processos: Lista de processos
        
        Returns:
            str: JSON com dados formatados
        """
        export_data = {
            'export_date': datetime.now().isoformat(),
            'total': len(processos),
            'processos': processos
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def import_from_sync(self, json_data: str) -> Tuple[bool, Dict]:
        """
        Importa processos de sincronização
        
        Args:
            json_data: String JSON com dados
        
        Returns:
            Tuple[bool, Dict]: (sucesso, dados_importados)
        """
        try:
            data = json.loads(json_data)
            return True, {
                'total': data.get('total', 0),
                'processos': data.get('processos', []),
                'import_date': datetime.now().isoformat()
            }
        except json.JSONDecodeError as e:
            error_msg = f"Erro ao importar dados: {str(e)}"
            self.sync_errors.append(error_msg)
            return False, {'error': error_msg}

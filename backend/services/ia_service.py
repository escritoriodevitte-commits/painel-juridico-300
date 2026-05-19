"""
Serviço de Integração com IA para Geração de Peças Jurídicas
Integra GeradorPecas (IA) com fallback para geração local
"""

import sys
import os
from typing import Optional, Dict, List
from datetime import datetime

# Adicionar o caminho do projeto anterior para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from modules.ia.gerador import GeradorPecas, TIPOS_PECA

class IAService:
    """Serviço para gerenciar geração de peças jurídicas via IA ou template local"""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """Inicializa o serviço com API key da OpenAI (opcional)"""
        self.gerador = GeradorPecas(api_key=openai_api_key)
        self.openai_api_key = openai_api_key
    
    def atualizar_api_key(self, api_key: str):
        """Atualiza a API key da OpenAI"""
        self.openai_api_key = api_key
        self.gerador.atualizar_configuracao(api_key)
    
    def listar_tipos_peca(self) -> Dict[str, str]:
        """Retorna dicionário com tipos de peça disponíveis"""
        return {
            key: value['nome'] 
            for key, value in TIPOS_PECA.items()
        }
    
    def gerar_peca_juridica(
        self,
        tipo_peca: str,
        processo_numero: str,
        vara: str,
        reclamante: str,
        reclamada: str,
        valor_pedido: Optional[float] = None,
        tese_inicial: Optional[str] = None,
        tese_defesa: Optional[str] = None,
        status: Optional[str] = None,
        juiz_nome: Optional[str] = None,
        perfil_juiz: Optional[Dict] = None,
        jurisprudencia: Optional[List[Dict]] = None,
        instrucoes_adicionais: Optional[str] = None,
    ) -> Dict:
        """
        Gera uma peça jurídica usando IA ou template local
        
        Args:
            tipo_peca: Tipo de peça (ex: 'reclamatoria_trabalhista')
            processo_numero: Número do processo
            vara: Vara do processo
            reclamante: Nome do reclamante
            reclamada: Nome da reclamada
            valor_pedido: Valor da reclamação
            tese_inicial: Tese inicial do reclamante
            tese_defesa: Tese de defesa
            status: Status do processo
            juiz_nome: Nome do juiz
            perfil_juiz: Dict com perfil do juiz
            jurisprudencia: Lista de jurisprudências relevantes
            instrucoes_adicionais: Instruções adicionais para o advogado
        
        Returns:
            Dict com:
                - conteudo: conteúdo da peça gerada
                - tipo_peca: tipo da peça
                - gerado_por_ia: bool indicando se foi gerado por IA
                - timestamp: data/hora de geração
                - aviso: aviso se IA não disponível
        """
        
        # Montar dados do processo
        lawsuit_data = {
            'numero_processo': processo_numero,
            'vara': vara,
            'reclamante': reclamante,
            'reclamada': reclamada,
            'valor_pedido': valor_pedido,
            'tese_inicial': tese_inicial,
            'tese_defesa': tese_defesa,
            'status': status or 'EM TRAMITAÇÃO'
        }
        
        # Montar perfil do juiz se fornecido
        judge_data = None
        if juiz_nome or perfil_juiz:
            judge_data = perfil_juiz or {}
            if juiz_nome and 'name' not in judge_data:
                judge_data['name'] = juiz_nome
            if vara and 'vara' not in judge_data:
                judge_data['vara'] = vara
        
        # Montar jurisprudência se fornecida
        refs = jurisprudencia or []
        
        # Gerar peça
        try:
            conteudo = self.gerador.gerar_peca(
                lawsuit=lawsuit_data,
                judge=judge_data,
                refs=refs,
                tipo=tipo_peca,
                instrucoes=instrucoes_adicionais or ""
            )
            
            # Determinar se foi gerado por IA
            gerado_por_ia = self.gerador.is_available() and "[ERRO" not in conteudo
            
            aviso = None
            if not self.gerador.is_available():
                aviso = "⚠️ OpenAI API não configurada. Usando template local como fallback."
            
            return {
                'sucesso': True,
                'conteudo': conteudo,
                'tipo_peca': tipo_peca,
                'tipo_nome': TIPOS_PECA.get(tipo_peca, {}).get('nome', tipo_peca.upper()),
                'gerado_por_ia': gerado_por_ia,
                'timestamp': datetime.utcnow().isoformat(),
                'aviso': aviso
            }
        
        except Exception as e:
            return {
                'sucesso': False,
                'erro': f"Erro ao gerar peça: {str(e)}",
                'tipo_peca': tipo_peca,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def validar_tipo_peca(self, tipo: str) -> bool:
        """Valida se o tipo de peça é válido"""
        return tipo in TIPOS_PECA
    
    def status_ia(self) -> Dict:
        """Retorna status da integração com IA"""
        return {
            'ia_disponivel': self.gerador.is_available(),
            'modelo': self.gerador.model if self.gerador.is_available() else None,
            'api_key_configurada': bool(self.openai_api_key),
            'tipos_peca_disponiveis': len(TIPOS_PECA)
        }


# Instância global
_ia_service: Optional[IAService] = None

def get_ia_service(openai_api_key: Optional[str] = None) -> IAService:
    """Factory function para obter instância do serviço"""
    global _ia_service
    if _ia_service is None:
        _ia_service = IAService(openai_api_key)
    return _ia_service

def reset_ia_service():
    """Reset da instância global (para testes)"""
    global _ia_service
    _ia_service = None

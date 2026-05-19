#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Busca Global
Busca full-text em processos, clientes e referências jurídicas
"""

from typing import List, Dict, Tuple
from datetime import datetime


class GlobalSearch:
    """
    Gerenciador de busca global
    
    Fornece busca full-text em:
    - Processos (número, partes, teses)
    - Clientes (nome, CPF, telefone, email)
    - Referências jurídicas (título, ementa, trecho)
    """
    
    def __init__(self):
        """Inicializa o módulo de busca"""
        self.search_history = []
    
    def search_processos(self, processos: List[Dict], query: str) -> List[Dict]:
        """
        Busca em processos
        
        Args:
            processos: Lista de processos
            query: Termo de busca
        
        Returns:
            List[Dict]: Processos que correspondem à busca
        """
        query_lower = query.lower()
        results = []
        
        for processo in processos:
            # Campos a buscar
            searchable_fields = [
                processo.get('numero_processo', ''),
                processo.get('vara', ''),
                processo.get('reclamante', ''),
                processo.get('reclamada', ''),
                processo.get('tese_inicial', ''),
                processo.get('tese_defesa', ''),
                processo.get('resultado', ''),
                str(processo.get('status', '')),
            ]
            
            # Buscar em todos os campos
            for field in searchable_fields:
                if query_lower in field.lower():
                    results.append(processo)
                    break
        
        return results
    
    def search_clientes(self, clientes: List[Dict], query: str) -> List[Dict]:
        """
        Busca em clientes
        
        Args:
            clientes: Lista de clientes
            query: Termo de busca
        
        Returns:
            List[Dict]: Clientes que correspondem à busca
        """
        query_lower = query.lower()
        results = []
        
        for cliente in clientes:
            searchable_fields = [
                cliente.get('nome', ''),
                cliente.get('cpf', ''),
                cliente.get('telefone', ''),
                cliente.get('email', ''),
                cliente.get('endereco', ''),
                cliente.get('observacoes', ''),
            ]
            
            for field in searchable_fields:
                if query_lower in field.lower():
                    results.append(cliente)
                    break
        
        return results
    
    def search_referencias(self, referencias: List[Dict], query: str) -> List[Dict]:
        """
        Busca em referências jurídicas
        
        Args:
            referencias: Lista de referências
            query: Termo de busca
        
        Returns:
            List[Dict]: Referências que correspondem à busca
        """
        query_lower = query.lower()
        results = []
        
        for ref in referencias:
            searchable_fields = [
                ref.get('titulo', ''),
                ref.get('trecho', ''),
                ref.get('autor', ''),
                ref.get('fonte', ''),
                ref.get('tipo', ''),
                ref.get('tema', ''),
            ]
            
            for field in searchable_fields:
                if query_lower in field.lower():
                    results.append(ref)
                    break
        
        return results
    
    def global_search(self, query: str, processos: List[Dict], clientes: List[Dict], 
                     referencias: List[Dict]) -> Dict:
        """
        Busca global em todos os tipos
        
        Args:
            query: Termo de busca
            processos: Lista de processos
            clientes: Lista de clientes
            referencias: Lista de referências
        
        Returns:
            Dict com resultados de todos os tipos
        """
        results = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'processos': self.search_processos(processos, query),
            'clientes': self.search_clientes(clientes, query),
            'referencias': self.search_referencias(referencias, query),
            'total': 0
        }
        
        # Calcular total
        results['total'] = (len(results['processos']) + 
                          len(results['clientes']) + 
                          len(results['referencias']))
        
        # Registrar no histórico
        self.search_history.append({
            'query': query,
            'results': results['total'],
            'timestamp': results['timestamp']
        })
        
        return results
    
    def search_by_type(self, query: str, data_type: str, data: List[Dict]) -> List[Dict]:
        """
        Busca por tipo específico
        
        Args:
            query: Termo de busca
            data_type: 'processos', 'clientes' ou 'referencias'
            data: Lista de dados
        
        Returns:
            List[Dict]: Resultados
        """
        if data_type == 'processos':
            return self.search_processos(data, query)
        elif data_type == 'clientes':
            return self.search_clientes(data, query)
        elif data_type == 'referencias':
            return self.search_referencias(data, query)
        else:
            return []
    
    def advanced_search(self, processos: List[Dict], filters: Dict) -> List[Dict]:
        """
        Busca avançada com múltiplos filtros
        
        Args:
            processos: Lista de processos
            filters: Dicionário com filtros
                - status: string ou lista
                - vara: string
                - reclamante: string
                - reclamada: string
                - data_inicio: DD/MM/AAAA
                - data_fim: DD/MM/AAAA
        
        Returns:
            List[Dict]: Processos filtrados
        """
        results = processos.copy()
        
        # Filtrar por status
        if filters.get('status'):
            status_filter = filters['status']
            if isinstance(status_filter, str):
                results = [p for p in results if p.get('status') == status_filter]
            elif isinstance(status_filter, list):
                results = [p for p in results if p.get('status') in status_filter]
        
        # Filtrar por vara
        if filters.get('vara'):
            vara_lower = filters['vara'].lower()
            results = [p for p in results if vara_lower in p.get('vara', '').lower()]
        
        # Filtrar por reclamante
        if filters.get('reclamante'):
            reclamante_lower = filters['reclamante'].lower()
            results = [p for p in results if reclamante_lower in p.get('reclamante', '').lower()]
        
        # Filtrar por reclamada
        if filters.get('reclamada'):
            reclamada_lower = filters['reclamada'].lower()
            results = [p for p in results if reclamada_lower in p.get('reclamada', '').lower()]
        
        # Filtrar por intervalo de datas
        if filters.get('data_inicio') or filters.get('data_fim'):
            results = self._filter_by_date_range(results, 
                                                 filters.get('data_inicio'),
                                                 filters.get('data_fim'))
        
        return results
    
    def _filter_by_date_range(self, processos: List[Dict], data_inicio: str, data_fim: str) -> List[Dict]:
        """
        Filtra processos por intervalo de datas
        
        Args:
            processos: Lista de processos
            data_inicio: Data inicial (DD/MM/AAAA)
            data_fim: Data final (DD/MM/AAAA)
        
        Returns:
            List[Dict]: Processos filtrados
        """
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                parts = date_str.split('/')
                return (int(parts[2]), int(parts[1]), int(parts[0]))  # (AAAA, MM, DD)
            except:
                return None
        
        inicio = parse_date(data_inicio)
        fim = parse_date(data_fim)
        
        results = []
        for processo in processos:
            proc_date = parse_date(processo.get('data_distribuicao'))
            
            if proc_date:
                if inicio and fim:
                    if inicio <= proc_date <= fim:
                        results.append(processo)
                elif inicio:
                    if proc_date >= inicio:
                        results.append(processo)
                elif fim:
                    if proc_date <= fim:
                        results.append(processo)
        
        return results
    
    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """
        Retorna histórico de buscas
        
        Args:
            limit: Número máximo de resultados
        
        Returns:
            List[Dict]: Histórico de buscas
        """
        return self.search_history[-limit:]
    
    def get_suggestions(self, query: str, data: Dict) -> List[str]:
        """
        Gera sugestões de busca baseadas nos dados
        
        Args:
            query: Termo de busca parcial
            data: Dicionário com listas de dados
                - 'processos': lista de processos
                - 'clientes': lista de clientes
        
        Returns:
            List[str]: Sugestões
        """
        suggestions = set()
        query_lower = query.lower()
        
        # Sugestões de processos
        if data.get('processos'):
            for processo in data['processos']:
                numero = processo.get('numero_processo', '')
                reclamante = processo.get('reclamante', '')
                reclamada = processo.get('reclamada', '')
                
                if query_lower in numero.lower():
                    suggestions.add(numero)
                if query_lower in reclamante.lower():
                    suggestions.add(reclamante)
                if query_lower in reclamada.lower():
                    suggestions.add(reclamada)
        
        # Sugestões de clientes
        if data.get('clientes'):
            for cliente in data['clientes']:
                nome = cliente.get('nome', '')
                if query_lower in nome.lower():
                    suggestions.add(nome)
        
        return sorted(list(suggestions))[:10]  # Top 10 sugestões
    
    def export_search_results(self, results: Dict) -> str:
        """
        Exporta resultados de busca em formato texto
        
        Args:
            results: Dicionário com resultados
        
        Returns:
            str: Resultados formatados
        """
        output = f"RESULTADOS DE BUSCA\n"
        output += f"Query: {results.get('query')}\n"
        output += f"Data: {results.get('timestamp')}\n"
        output += f"Total: {results.get('total')} resultados\n\n"
        
        # Processos
        output += f"PROCESSOS ({len(results.get('processos', []))}):\n"
        for p in results.get('processos', [])[:5]:
            output += f"  - {p.get('numero_processo')} ({p.get('status')})\n"
        
        # Clientes
        output += f"\nCLIENTES ({len(results.get('clientes', []))}):\n"
        for c in results.get('clientes', [])[:5]:
            output += f"  - {c.get('nome')} ({c.get('cpf', 'S/CPF')})\n"
        
        # Referências
        output += f"\nREFERÊNCIAS ({len(results.get('referencias', []))}):\n"
        for r in results.get('referencias', [])[:5]:
            output += f"  - {r.get('titulo')} ({r.get('tipo')})\n"
        
        return output

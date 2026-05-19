#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Integração de Validadores com Interface
Funções para validar campos de entrada dos formulários com mensagens amigáveis
"""

from modules.validators.date_validator import DateValidator
from modules.validators.number_validator import NumberValidator
from modules.validators.document_validator import DocumentValidator
from typing import Tuple


class FormValidator:
    """
    Validador de formulários para Painel Jurídico
    
    Fornece métodos para validar campos específicos dos formulários:
    - Processo (número, vara, datas, valores)
    - Cliente (nome, CPF, telefone, email)
    - Acordo (valores, datas, documentos)
    """
    
    @staticmethod
    def validate_processo_fields(data: dict) -> Tuple[bool, str]:
        """
        Valida campos obrigatórios de um processo
        
        Args:
            data: Dicionário com campos do processo
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
        """
        # Validar obrigatórios
        required = ['numero_processo', 'vara', 'reclamante', 'reclamada']
        for field in required:
            if not data.get(field):
                return False, f"Campo obrigatório: {field}"
        
        # Validar datas se preenchidas
        if data.get('data_distribuicao'):
            valid, msg = DateValidator.validate_date(data['data_distribuicao'], allow_future=False)
            if not valid:
                return False, f"Data de distribuição inválida: {msg}"
        
        if data.get('data_encerramento'):
            valid, msg = DateValidator.validate_date(data['data_encerramento'], allow_future=True)
            if not valid:
                return False, f"Data de encerramento inválida: {msg}"
        
        # Validar que encerramento >= distribuição
        if data.get('data_distribuicao') and data.get('data_encerramento'):
            valid, msg = DateValidator.validate_date_range(
                data['data_distribuicao'],
                data['data_encerramento']
            )
            if not valid:
                return False, f"Intervalo de datas inválido: data de encerramento deve ser posterior à de distribuição"
        
        # Validar valores monetários
        for field in ['valor_pedido', 'valor_obtido']:
            if data.get(field):
                valid, msg = NumberValidator.validate_currency(f"R$ {data[field]}")
                if not valid:
                    return False, f"{field} inválido: {msg}"
        
        return True, ""
    
    @staticmethod
    def validate_cliente_fields(data: dict) -> Tuple[bool, str]:
        """
        Valida campos de um cliente
        
        Args:
            data: Dicionário com campos do cliente
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
        """
        # Validar obrigatórios
        if not data.get('nome'):
            return False, "Nome do cliente é obrigatório"
        
        # Validar CPF se preenchido
        if data.get('cpf'):
            valid, msg = DocumentValidator.validate_cpf(data['cpf'])
            if not valid:
                return False, f"CPF inválido: {msg}"
        
        # Validar email se preenchido (simples)
        if data.get('email'):
            if '@' not in data['email'] or '.' not in data['email'].split('@')[-1]:
                return False, "Email inválido"
        
        # Validar telefone se preenchido (apenas validação de caracteres)
        if data.get('telefone'):
            clean = ''.join(c for c in data['telefone'] if c.isdigit())
            if len(clean) < 10 or len(clean) > 11:
                return False, "Telefone deve ter 10 ou 11 dígitos"
        
        return True, ""
    
    @staticmethod
    def validate_acordo_fields(data: dict) -> Tuple[bool, str]:
        """
        Valida campos de um acordo/sentença
        
        Args:
            data: Dicionário com campos do acordo
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
        """
        # Validar obrigatórios
        if not data.get('tipo'):
            return False, "Tipo de acordo é obrigatório"
        
        # Validar valores se preenchidos
        for field in ['valor_pedido', 'valor_obtido']:
            if data.get(field):
                valid, msg = NumberValidator.validate_currency(f"R$ {data[field]}")
                if not valid:
                    return False, f"{field} inválido: {msg}"
        
        # Validar que valor_obtido <= valor_pedido
        if data.get('valor_pedido') and data.get('valor_obtido'):
            try:
                pedido = float(str(data['valor_pedido']).replace(',', '.'))
                obtido = float(str(data['valor_obtido']).replace(',', '.'))
                if obtido > pedido:
                    return False, "Valor obtido não pode ser maior que valor pedido"
            except:
                pass
        
        # Validar data se preenchida
        if data.get('data_homologacao'):
            valid, msg = DateValidator.validate_date(data['data_homologacao'], allow_future=True)
            if not valid:
                return False, f"Data de homologação inválida: {msg}"
        
        return True, ""
    
    @staticmethod
    def format_for_display(field_type: str, value: str) -> str:
        """
        Formata um valor para exibição conforme seu tipo
        
        Args:
            field_type: Tipo do campo ('currency', 'cpf', 'cnpj', 'date')
            value: Valor a formatar
        
        Returns:
            str: Valor formatado
        """
        if not value:
            return ""
        
        if field_type == 'currency':
            return NumberValidator.format_currency(value)
        elif field_type == 'cpf':
            return DocumentValidator.format_cpf(value)
        elif field_type == 'cnpj':
            return DocumentValidator.format_cnpj(value)
        elif field_type == 'date':
            return DateValidator.format_date(value, output_format="%d/%m/%Y")
        else:
            return value
    
    @staticmethod
    def validate_field(field_type: str, value: str) -> Tuple[bool, str]:
        """
        Valida um campo individual conforme seu tipo
        
        Args:
            field_type: Tipo do campo ('date', 'currency', 'percentage', 'cpf', 'cnpj', 'email')
            value: Valor a validar
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
        """
        if not value:
            return True, ""  # Campo vazio é válido (use required flag para obrigatório)
        
        if field_type == 'date':
            return DateValidator.validate_date(value, allow_future=False)
        elif field_type == 'date_future':
            return DateValidator.validate_date(value, allow_future=True)
        elif field_type == 'currency':
            return NumberValidator.validate_currency(value)
        elif field_type == 'percentage':
            return NumberValidator.validate_percentage(value)
        elif field_type == 'cpf':
            return DocumentValidator.validate_cpf(value)
        elif field_type == 'cnpj':
            return DocumentValidator.validate_cnpj(value)
        elif field_type == 'email':
            if '@' not in value or '.' not in value.split('@')[-1]:
                return False, "Email inválido"
            return True, ""
        elif field_type == 'phone':
            clean = ''.join(c for c in value if c.isdigit())
            if len(clean) < 10 or len(clean) > 11:
                return False, "Telefone deve ter 10 ou 11 dígitos"
            return True, ""
        else:
            return True, ""

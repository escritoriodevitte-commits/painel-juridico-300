#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validador de Documentos Brasileiros
Validação de CPF e CNPJ com verificação de checksum
"""

from typing import Tuple
import re


class DocumentValidator:
    """
    Validador de documentos brasileiros
    
    Fornece métodos para validar:
    - CPF (Cadastro de Pessoas Físicas)
    - CNPJ (Cadastro Nacional de Pessoa Jurídica)
    """
    
    @staticmethod
    def validate_cpf(cpf: str) -> Tuple[bool, str]:
        """
        Valida CPF (Cadastro de Pessoas Físicas)
        
        Aceita formatos:
        - "123.456.789-09"
        - "12345678909"
        
        Args:
            cpf: String contendo o CPF
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
        """
        try:
            if not cpf or not isinstance(cpf, str):
                return False, "CPF deve ser uma string"
            
            # Remove formatação
            cpf_clean = re.sub(r'\D', '', cpf)
            
            # Validar tamanho
            if len(cpf_clean) != 11:
                return False, "CPF deve ter 11 dígitos"
            
            # Verificar se é sequência de dígitos iguais (inválido)
            if cpf_clean == cpf_clean[0] * 11:
                return False, "CPF inválido (sequência de dígitos iguais)"
            
            # Validar primeiro dígito verificador
            sum1 = sum(int(cpf_clean[i]) * (10 - i) for i in range(9))
            digit1 = 11 - (sum1 % 11)
            digit1 = 0 if digit1 > 9 else digit1
            
            if int(cpf_clean[9]) != digit1:
                return False, "CPF inválido (dígito verificador incorreto)"
            
            # Validar segundo dígito verificador
            sum2 = sum(int(cpf_clean[i]) * (11 - i) for i in range(10))
            digit2 = 11 - (sum2 % 11)
            digit2 = 0 if digit2 > 9 else digit2
            
            if int(cpf_clean[10]) != digit2:
                return False, "CPF inválido (dígito verificador incorreto)"
            
            return True, ""
        
        except Exception as e:
            return False, f"Erro ao validar CPF: {str(e)}"
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> Tuple[bool, str]:
        """
        Valida CNPJ (Cadastro Nacional de Pessoa Jurídica)
        
        Aceita formatos:
        - "12.345.678/0001-90"
        - "12345678000190"
        
        Args:
            cnpj: String contendo o CNPJ
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
        """
        try:
            if not cnpj or not isinstance(cnpj, str):
                return False, "CNPJ deve ser uma string"
            
            # Remove formatação
            cnpj_clean = re.sub(r'\D', '', cnpj)
            
            # Validar tamanho
            if len(cnpj_clean) != 14:
                return False, "CNPJ deve ter 14 dígitos"
            
            # Verificar se é sequência de dígitos iguais (inválido)
            if cnpj_clean == cnpj_clean[0] * 14:
                return False, "CNPJ inválido (sequência de dígitos iguais)"
            
            # Validar primeiro dígito verificador
            weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            sum1 = sum(int(cnpj_clean[i]) * weights1[i] for i in range(12))
            remainder1 = sum1 % 11
            digit1 = 0 if remainder1 < 2 else 11 - remainder1
            
            if int(cnpj_clean[12]) != digit1:
                return False, "CNPJ inválido (dígito verificador incorreto)"
            
            # Validar segundo dígito verificador
            weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            sum2 = sum(int(cnpj_clean[i]) * weights2[i] for i in range(13))
            remainder2 = sum2 % 11
            digit2 = 0 if remainder2 < 2 else 11 - remainder2
            
            if int(cnpj_clean[13]) != digit2:
                return False, "CNPJ inválido (dígito verificador incorreto)"
            
            return True, ""
        
        except Exception as e:
            return False, f"Erro ao validar CNPJ: {str(e)}"
    
    @staticmethod
    def format_cpf(cpf: str) -> str:
        """
        Formata um CPF para o padrão 123.456.789-09
        
        Args:
            cpf: CPF com ou sem formatação
        
        Returns:
            str: CPF formatado ou string original se erro
        """
        try:
            cpf_clean = re.sub(r'\D', '', cpf)
            if len(cpf_clean) != 11:
                return cpf
            return f"{cpf_clean[:3]}.{cpf_clean[3:6]}.{cpf_clean[6:9]}-{cpf_clean[9:]}"
        except:
            return cpf
    
    @staticmethod
    def format_cnpj(cnpj: str) -> str:
        """
        Formata um CNPJ para o padrão 12.345.678/0001-90
        
        Args:
            cnpj: CNPJ com ou sem formatação
        
        Returns:
            str: CNPJ formatado ou string original se erro
        """
        try:
            cnpj_clean = re.sub(r'\D', '', cnpj)
            if len(cnpj_clean) != 14:
                return cnpj
            return f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"
        except:
            return cnpj

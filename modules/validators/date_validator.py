#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validador de Datas
Validação de datas em formato DD/MM/AAAA com suporte a ranges
"""

from datetime import datetime
from typing import Tuple


class DateValidator:
    """
    Validador de datas no formato DD/MM/AAAA
    
    Fornece métodos para validar:
    - Formato de data
    - Data válida (dia/mês/ano existentes)
    - Range de datas
    - Datas futuras/passadas
    """
    
    # Formato esperado
    DATE_FORMAT = "%d/%m/%Y"
    
    @staticmethod
    def validate_date(date_str: str, allow_future: bool = False) -> Tuple[bool, str]:
        """
        Valida uma data no formato DD/MM/AAAA
        
        Args:
            date_str: String contendo a data (formato: DD/MM/AAAA)
            allow_future: Se True, permite datas futuras
        
        Returns:
            Tuple[bool, str]: (True, "") se válida, (False, "motivo") se inválida
            
        Examples:
            >>> DateValidator.validate_date("19/05/2026")
            (True, "")
            
            >>> DateValidator.validate_date("32/13/2026")
            (False, "Data inválida: day is out of range for month")
        """
        try:
            # Validar formato
            if not date_str or not isinstance(date_str, str):
                return False, "Data deve ser uma string"
            
            date_str = date_str.strip()
            
            if len(date_str) != 10:
                return False, "Formato deve ser DD/MM/AAAA (10 caracteres)"
            
            # Tentar converter
            date_obj = datetime.strptime(date_str, DateValidator.DATE_FORMAT)
            
            # Validar data futura se necessário
            if not allow_future:
                today = datetime.today()
                if date_obj > today:
                    return False, "Data não pode ser no futuro"
            
            return True, ""
            
        except ValueError as e:
            error_msg = str(e)
            
            # Mensagens amigáveis
            if "unconverted data remains" in error_msg:
                return False, "Formato inválido: use DD/MM/AAAA"
            elif "time data" in error_msg:
                return False, "Data inválida (verifique dia/mês/ano)"
            elif "month must be in" in error_msg:
                return False, "Mês deve estar entre 01 e 12"
            elif "day is out of range" in error_msg:
                return False, "Dia inválido para este mês"
            else:
                return False, f"Data inválida: {error_msg}"
        
        except Exception as e:
            return False, f"Erro ao validar data: {str(e)}"
    
    @staticmethod
    def validate_date_range(start_str: str, end_str: str) -> Tuple[bool, str]:
        """
        Valida um range de datas (start <= end)
        
        Args:
            start_str: Data inicial (formato: DD/MM/AAAA)
            end_str: Data final (formato: DD/MM/AAAA)
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
            
        Examples:
            >>> DateValidator.validate_date_range("01/01/2024", "31/12/2024")
            (True, "")
            
            >>> DateValidator.validate_date_range("31/12/2024", "01/01/2024")
            (False, "Data final deve ser posterior à data inicial")
        """
        # Validar data inicial
        valid_start, err_start = DateValidator.validate_date(start_str, allow_future=True)
        if not valid_start:
            return False, f"Data inicial inválida: {err_start}"
        
        # Validar data final
        valid_end, err_end = DateValidator.validate_date(end_str, allow_future=True)
        if not valid_end:
            return False, f"Data final inválida: {err_end}"
        
        # Comparar datas
        d1 = datetime.strptime(start_str, DateValidator.DATE_FORMAT)
        d2 = datetime.strptime(end_str, DateValidator.DATE_FORMAT)
        
        if d2 < d1:
            return False, "Data final deve ser posterior ou igual à data inicial"
        
        return True, ""
    
    @staticmethod
    def validate_date_not_future(date_str: str) -> Tuple[bool, str]:
        """
        Valida que a data não seja futura
        
        Args:
            date_str: String contendo a data (formato: DD/MM/AAAA)
        
        Returns:
            Tuple[bool, str]: (True, "") se válida e não futura
        """
        return DateValidator.validate_date(date_str, allow_future=False)
    
    @staticmethod
    def validate_date_in_past(date_str: str, days: int = 0) -> Tuple[bool, str]:
        """
        Valida que a data seja no passado (antes de N dias)
        
        Args:
            date_str: String contendo a data (formato: DD/MM/AAAA)
            days: Número de dias no futuro permitidos (padrão: 0)
        
        Returns:
            Tuple[bool, str]: (True, "") se válida e no passado
        """
        try:
            valid, err = DateValidator.validate_date(date_str, allow_future=True)
            if not valid:
                return False, err
            
            date_obj = datetime.strptime(date_str, DateValidator.DATE_FORMAT)
            from datetime import timedelta
            
            allowed_date = datetime.today() + timedelta(days=days)
            
            if date_obj > allowed_date:
                if days == 0:
                    return False, "Data deve ser anterior ao dia de hoje"
                else:
                    return False, f"Data deve ser anterior aos próximos {days} dias"
            
            return True, ""
        
        except Exception as e:
            return False, f"Erro ao validar data: {str(e)}"
    
    @staticmethod
    def format_date(date_str: str, input_format: str = None, output_format: str = "%d/%m/%Y") -> str:
        """
        Converte uma data para um formato diferente
        
        Args:
            date_str: String contendo a data
            input_format: Formato de entrada (padrão: "%d/%m/%Y")
            output_format: Formato de saída (padrão: "%d/%m/%Y")
        
        Returns:
            str: Data formatada ou string original se erro
        """
        try:
            if input_format is None:
                input_format = DateValidator.DATE_FORMAT
            
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        
        except Exception as e:
            return date_str  # Retorna original se erro
    
    @staticmethod
    def get_age(birth_date_str: str) -> Tuple[int, str]:
        """
        Calcula a idade a partir de uma data de nascimento
        
        Args:
            birth_date_str: Data de nascimento (formato: DD/MM/AAAA)
        
        Returns:
            Tuple[int, str]: (idade, "") se válido, (-1, "erro") se inválido
        """
        try:
            valid, err = DateValidator.validate_date(birth_date_str, allow_future=False)
            if not valid:
                return -1, err
            
            birth_date = datetime.strptime(birth_date_str, DateValidator.DATE_FORMAT)
            today = datetime.today()
            
            age = today.year - birth_date.year
            
            # Ajustar se ainda não completou aniversário este ano
            if (today.month, today.day) < (birth_date.month, birth_date.day):
                age -= 1
            
            return age, ""
        
        except Exception as e:
            return -1, f"Erro ao calcular idade: {str(e)}"

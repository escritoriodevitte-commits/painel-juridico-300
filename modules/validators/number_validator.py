#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Validador de Números
Validação de valores monetários, percentuais e numéricos
"""

from typing import Tuple


class NumberValidator:
    """
    Validador de valores numéricos brasileiros
    
    Fornece métodos para validar:
    - Moeda brasileira (R$)
    - Percentuais (0-100%)
    - Números positivos/negativos
    - Ranges numéricos
    """
    
    @staticmethod
    def validate_currency(value: str) -> Tuple[bool, str]:
        """
        Valida formato de moeda brasileira (R$)
        
        Aceita formatos:
        - "1000"
        - "1.000,00"
        - "R$ 1.000,00"
        - "1000,00"
        
        Args:
            value: String contendo o valor monetário
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
            
        Examples:
            >>> NumberValidator.validate_currency("1.000,00")
            (True, "")
            
            >>> NumberValidator.validate_currency("1000.00")
            (False, "Formato inválido...")
        """
        try:
            if not value or not isinstance(value, str):
                return False, "Valor deve ser uma string"
            
            # Remove R$ e espaços
            clean = value.replace("R$", "").replace("R $", "").strip()
            
            # Converte para padrão Python (ponto como separador decimal)
            # Formato brasileiro: 1.000,00 -> 1000.00
            clean = clean.replace(".", "")  # Remove separador de milhares
            clean = clean.replace(",", ".")  # Converte vírgula para ponto
            
            float_value = float(clean)
            
            # Validar valor positivo
            if float_value < 0:
                return False, "Valor não pode ser negativo"
            
            return True, ""
            
        except ValueError:
            return False, "Formato de moeda inválido. Use: 1.000,00 ou R$ 1.000,00"
        except Exception as e:
            return False, f"Erro ao validar moeda: {str(e)}"
    
    @staticmethod
    def validate_percentage(value) -> Tuple[bool, str]:
        """
        Valida percentual (0-100)
        
        Args:
            value: String ou número com o percentual
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
            
        Examples:
            >>> NumberValidator.validate_percentage("50")
            (True, "")
            
            >>> NumberValidator.validate_percentage("150")
            (False, "Percentual deve estar entre 0 e 100")
        """
        try:
            # Converter para float
            if isinstance(value, str):
                # Remove símbolo % se presente
                clean_value = value.replace("%", "").strip()
                percent = float(clean_value)
            else:
                percent = float(value)
            
            # Validar range
            if not (0 <= percent <= 100):
                return False, "Percentual deve estar entre 0 e 100"
            
            return True, ""
            
        except (ValueError, TypeError):
            return False, "Valor percentual inválido. Use um número entre 0 e 100"
        except Exception as e:
            return False, f"Erro ao validar percentual: {str(e)}"
    
    @staticmethod
    def validate_number(value, min_value=None, max_value=None, allow_negative=True) -> Tuple[bool, str]:
        """
        Valida um número genérico com range opcional
        
        Args:
            value: String ou número
            min_value: Valor mínimo permitido (opcional)
            max_value: Valor máximo permitido (opcional)
            allow_negative: Se False, rejeita negativos
        
        Returns:
            Tuple[bool, str]: (True, "") se válido, (False, "motivo") se inválido
        """
        try:
            if isinstance(value, str):
                num = float(value.strip())
            else:
                num = float(value)
            
            # Validar se permite negativos
            if not allow_negative and num < 0:
                return False, "Valor não pode ser negativo"
            
            # Validar mínimo
            if min_value is not None and num < min_value:
                return False, f"Valor deve ser maior ou igual a {min_value}"
            
            # Validar máximo
            if max_value is not None and num > max_value:
                return False, f"Valor deve ser menor ou igual a {max_value}"
            
            return True, ""
            
        except (ValueError, TypeError):
            return False, "Valor numérico inválido"
        except Exception as e:
            return False, f"Erro ao validar número: {str(e)}"
    
    @staticmethod
    def parse_currency(value: str) -> float:
        """
        Extrai o valor numérico de uma string de moeda
        
        Args:
            value: String contendo a moeda
        
        Returns:
            float: Valor convertido ou 0.0 se erro
            
        Examples:
            >>> NumberValidator.parse_currency("R$ 1.000,00")
            1000.0
        """
        try:
            # Remove R$ e espaços
            clean = value.replace("R$", "").replace("R $", "").strip()
            
            # Converte para padrão Python
            clean = clean.replace(".", "")
            clean = clean.replace(",", ".")
            
            return float(clean)
        
        except:
            return 0.0
    
    @staticmethod
    def format_currency(value) -> str:
        """
        Formata um número como moeda brasileira
        
        Args:
            value: Número a ser formatado
        
        Returns:
            str: Valor formatado (ex: "R$ 1.000,00")
            
        Examples:
            >>> NumberValidator.format_currency(1000)
            'R$ 1.000,00'
        """
        try:
            num = float(value)
            # Formatar com 2 casas decimais
            formatted = f"{num:,.2f}"
            # Converter separadores para padrão brasileiro
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {formatted}"
        
        except:
            return "R$ 0,00"
    
    @staticmethod
    def validate_integer(value) -> Tuple[bool, str]:
        """
        Valida se um valor é um número inteiro
        
        Args:
            value: String ou número
        
        Returns:
            Tuple[bool, str]: (True, "") se válido inteiro
        """
        try:
            if isinstance(value, str):
                int_value = int(value.strip())
            else:
                int_value = int(value)
            
            return True, ""
        
        except (ValueError, TypeError):
            return False, "Valor deve ser um número inteiro"
        except Exception as e:
            return False, f"Erro ao validar inteiro: {str(e)}"
    
    @staticmethod
    def validate_decimal(value, decimal_places=2) -> Tuple[bool, str]:
        """
        Valida se um valor é um decimal com número específico de casas
        
        Args:
            value: String ou número
            decimal_places: Número de casas decimais esperadas
        
        Returns:
            Tuple[bool, str]: (True, "") se válido
        """
        try:
            if isinstance(value, str):
                dec_value = float(value.strip())
            else:
                dec_value = float(value)
            
            # Validar número de casas decimais
            str_value = str(dec_value)
            if "." in str_value:
                decimals = len(str_value.split(".")[1])
                if decimals > decimal_places:
                    return False, f"Máximo {decimal_places} casas decimais"
            
            return True, ""
        
        except (ValueError, TypeError):
            return False, f"Valor deve ser um decimal com até {decimal_places} casas"
        except Exception as e:
            return False, f"Erro ao validar decimal: {str(e)}"

"""
Legal AI Client - Integração com Backend API
Consome endpoints do Legal AI (FastAPI) para análises NLP, documentos, etc.
"""
import requests
from typing import Optional, Dict, List, Any
from datetime import datetime


class LegalAIClient:
    """Cliente para integração com API do Legal AI"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Inicializa o cliente com a URL base da API
        
        Args:
            base_url: URL base do backend Legal AI (padrão: localhost:8000)
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = 30
        self.session = requests.Session()
        self.connected = False

    def test_connection(self) -> bool:
        """Testa conexão com o servidor Legal AI"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=5
            )
            self.connected = response.status_code == 200
            return self.connected
        except Exception as e:
            self.connected = False
            return False

    def get_health(self) -> Dict[str, Any]:
        """Obtém status de saúde da API"""
        try:
            response = self.session.get(
                f"{self.base_url}/health",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else {"status": "offline"}
        except Exception:
            return {"status": "offline", "error": "Conexão falhou"}

    # ==================== PROCESSOS ====================

    def create_lawsuit_remote(self, data: Dict) -> Optional[Dict]:
        """Cria processo no Legal AI e sincroniza"""
        try:
            payload = {
                'numero_processo': data.get('numero_processo'),
                'vara': data.get('vara'),
                'reclamante': data.get('reclamante'),
                'reclamada': data.get('reclamada'),
                'valor_pedido': data.get('valor_pedido'),
                'status': data.get('status', 'em_andamento'),
                'tese_inicial': data.get('tese_inicial'),
                'data_distribuicao': data.get('data_distribuicao'),
            }
            response = self.session.post(
                f"{self.base_url}/processes",
                json=payload,
                timeout=self.timeout
            )
            return response.json() if response.status_code in (200, 201) else None
        except Exception as e:
            return None

    def get_lawsuits_remote(self) -> List[Dict]:
        """Obtém todos os processos do Legal AI"""
        try:
            response = self.session.get(
                f"{self.base_url}/processes",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []

    def get_lawsuit_by_number(self, numero_processo: str) -> Optional[Dict]:
        """Busca processo por número no Legal AI"""
        try:
            response = self.session.get(
                f"{self.base_url}/processes/search",
                params={'numero': numero_processo},
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    # ==================== DOCUMENTOS ====================

    def upload_document(self, lawsuit_id: int, file_path: str, doc_type: str) -> Optional[Dict]:
        """Upload de documento para análise NLP"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {'lawsuit_id': lawsuit_id, 'tipo': doc_type}
                response = self.session.post(
                    f"{self.base_url}/documents/upload",
                    files=files,
                    data=data,
                    timeout=60
                )
            return response.json() if response.status_code in (200, 201) else None
        except Exception:
            return None

    def get_document_analysis(self, document_id: int) -> Optional[Dict]:
        """Obtém análise NLP de um documento"""
        try:
            response = self.session.get(
                f"{self.base_url}/documents/{document_id}/analysis",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def get_lawsuit_documents(self, lawsuit_id: int) -> List[Dict]:
        """Lista todos os documentos de um processo"""
        try:
            response = self.session.get(
                f"{self.base_url}/lawsuits/{lawsuit_id}/documents",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []

    # ==================== ANÁLISES NLP ====================

    def analyze_text(self, text: str, analysis_type: str = "full") -> Optional[Dict]:
        """Realiza análise NLP em texto (entidades, classificação, sentimento, resumo)"""
        try:
            payload = {
                'text': text,
                'type': analysis_type
            }
            response = self.session.post(
                f"{self.base_url}/analysis/nlp",
                json=payload,
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def extract_entities(self, text: str) -> Optional[Dict]:
        """Extrai entidades (pessoas, datas, valores, etc.)"""
        try:
            payload = {'text': text}
            response = self.session.post(
                f"{self.base_url}/analysis/entities",
                json=payload,
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def classify_document(self, text: str) -> Optional[Dict]:
        """Classifica o tipo de documento (reclamatória, contestação, etc.)"""
        try:
            payload = {'text': text}
            response = self.session.post(
                f"{self.base_url}/analysis/classify",
                json=payload,
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def analyze_sentiment(self, text: str) -> Optional[Dict]:
        """Analisa sentimento do texto"""
        try:
            payload = {'text': text}
            response = self.session.post(
                f"{self.base_url}/analysis/sentiment",
                json=payload,
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def summarize_text(self, text: str, max_length: int = 500) -> Optional[str]:
        """Gera resumo automático do texto"""
        try:
            payload = {'text': text, 'max_length': max_length}
            response = self.session.post(
                f"{self.base_url}/analysis/summarize",
                json=payload,
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('summary')
            return None
        except Exception:
            return None

    # ==================== SEARCH ====================

    def search_documents(self, query: str, lawsuit_id: Optional[int] = None) -> List[Dict]:
        """Busca documentos por texto (full-text search)"""
        try:
            params = {'q': query}
            if lawsuit_id:
                params['lawsuit_id'] = lawsuit_id
            response = self.session.get(
                f"{self.base_url}/search",
                params=params,
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else []
        except Exception:
            return []

    # ==================== RELATÓRIOS ====================

    def get_process_report(self, lawsuit_id: int) -> Optional[Dict]:
        """Gera relatório consolidado de um processo"""
        try:
            response = self.session.get(
                f"{self.base_url}/lawsuits/{lawsuit_id}/report",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def export_to_pdf(self, lawsuit_id: int, report_type: str = "full") -> Optional[bytes]:
        """Exporta relatório em PDF"""
        try:
            response = self.session.get(
                f"{self.base_url}/lawsuits/{lawsuit_id}/export/pdf",
                params={'type': report_type},
                timeout=self.timeout
            )
            return response.content if response.status_code == 200 else None
        except Exception:
            return None

    # ==================== SINCRONIZAÇÃO ====================

    def sync_lawsuit(self, local_lawsuit: Dict) -> Optional[Dict]:
        """Sincroniza processo local com Legal AI"""
        try:
            response = self.session.post(
                f"{self.base_url}/sync/lawsuit",
                json=local_lawsuit,
                timeout=self.timeout
            )
            return response.json() if response.status_code in (200, 201) else None
        except Exception:
            return None

    def get_sync_status(self) -> Dict[str, Any]:
        """Obtém status de sincronização"""
        try:
            response = self.session.get(
                f"{self.base_url}/sync/status",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else {"synced": False}
        except Exception:
            return {"synced": False, "error": "Conexão falhou"}

    # ==================== CONFIGURAÇÃO ====================

    def update_server_url(self, url: str) -> None:
        """Atualiza URL do servidor"""
        self.base_url = url.rstrip("/")
        self.test_connection()

    def get_server_info(self) -> Optional[Dict]:
        """Obtém informações do servidor"""
        try:
            response = self.session.get(
                f"{self.base_url}/info",
                timeout=self.timeout
            )
            return response.json() if response.status_code == 200 else None
        except Exception:
            return None

    def set_timeout(self, seconds: int) -> None:
        """Define timeout para requisições"""
        self.timeout = seconds

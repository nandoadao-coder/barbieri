import httpx
from app.config import settings


class UazapiClient:
    def __init__(self):
        self.base_url = settings.uazapi_base_url.rstrip("/")
        self.token = settings.uazapi_token
        self.instance = settings.uazapi_instance
        self.headers = {"Authorization": self.token, "Content-Type": "application/json"}

    def send_text(self, phone: str, message: str) -> bool:
        """Envia mensagem de texto. Retorna True se sucesso."""
        url = f"{self.base_url}/message/sendText/{self.instance}"
        payload = {
            "number": phone,
            "text": message,
        }
        response = httpx.post(url, json=payload, headers=self.headers, timeout=10)
        return response.status_code == 200

    def send_document(self, phone: str, file_url: str, filename: str) -> bool:
        """Envia documento (PDF). Retorna True se sucesso."""
        url = f"{self.base_url}/message/sendMedia/{self.instance}"
        payload = {
            "number": phone,
            "mediatype": "document",
            "mimetype": "application/pdf",
            "media": file_url,
            "fileName": filename,
        }
        response = httpx.post(url, json=payload, headers=self.headers, timeout=10)
        return response.status_code == 200

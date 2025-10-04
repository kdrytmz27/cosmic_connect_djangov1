import requests
import logging
import json
from django.conf import settings
from requests.exceptions import RequestException, HTTPError

logger = logging.getLogger(__name__)

class CosmicAPIClient:
    def __init__(self):
        self.base_url = settings.COSMIC_API_BASE_URL
        self.api_key = settings.COSMIC_API_KEY
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint: str, payload: dict, accept_header: str = 'application/json'):
        if not all([self.base_url, self.api_key]):
            raise ValueError("Cosmic API URL veya API Anahtarı .env dosyasında ayarlanmamış.")

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        request_headers = self.headers.copy()
        request_headers['Accept'] = accept_header

        try:
            response = requests.post(url, headers=request_headers, json=payload, timeout=120)
            
            logger.info(f"Cosmic API İsteği Başarılı ({url}). Durum Kodu: {response.status_code}.")

            response.raise_for_status()
            
            return response.json() if accept_header == 'application/json' else response.content
        
        except HTTPError as http_err:
            logger.warning(
                "Cosmic API'den HTTP hatası alındı.\n"
                f"API Yanıtı: {response.text}"
            )
            raise
        
        except RequestException as req_err:
            logger.error(
                "Cosmic API'ye bağlanırken bir hata oluştu.\n"
                f"URL: {url}\n"
                f"Hata: {req_err}"
            )
            raise

    def get_full_chart_data(self, lat: float, lon: float, date: str, time: str):
        payload = {"lat": lat, "lon": lon, "date": date, "time": time}
        return self._make_request("natal/full-chart", payload)

    def get_wheel_chart_image(self, lat: float, lon: float, date: str, time: str):
        payload = {"lat": lat, "lon": lon, "date": date, "time": time}
        return self._make_request("natal/wheel-chart", payload, accept_header='image/png')
        
    def get_synastry_aspects(self, person1_data: dict, person2_data: dict):
        payload = {
            "person1": person1_data,
            "person2": person2_data
        }
        response_data = self._make_request("synastry/aspects", payload)
        return response_data.get('aspects', []) if isinstance(response_data, dict) else []

cosmic_api_client = CosmicAPIClient()
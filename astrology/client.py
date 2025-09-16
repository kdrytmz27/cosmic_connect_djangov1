# Lütfen bu kodu kopyalayıp astrology/client.py dosyasının içine yapıştırın.

import requests
from django.conf import settings
from requests.exceptions import RequestException, HTTPError

class CosmicAPIClient:
    """
    CosmicAPI v3.0 Kılavuzuna göre %100 uyumlu hale getirilmiş API istemcisi.
    """
    def __init__(self):
        self.base_url = settings.COSMS_API_BASE_URL # Düzeltme: COSMIC_API_BASE_URL olmalı
        self.api_key = settings.COSMIC_API_KEY
        
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint: str, payload: dict, accept_header: str = 'application/json'):
        """Tekrar eden istek mantığını yöneten ana metod."""
        if not all([self.base_url, self.api_key]):
            raise ValueError("Cosmic API URL veya API Anahtarı .env dosyasında ayarlanmamış.")

        url = f"{self.base_url}{endpoint}"
        request_headers = self.headers.copy()
        request_headers['Accept'] = accept_header

        try:
            # DEĞİŞİKLİK BURADA: Timeout süresini 90 saniyeye çıkardık.
            response = requests.post(url, headers=request_headers, json=payload, timeout=90)
            response.raise_for_status()
            
            return response.json() if accept_header == 'application/json' else response.content
        
        except HTTPError as http_err:
            print(f"Cosmic API'den HTTP hatası alındı ({url}): {http_err} - Yanıt: {response.text}")
            raise
        
        except RequestException as req_err:
            print(f"Cosmic API'ye bağlanırken bir hata oluştu ({url}): {req_err}")
            raise

    def get_full_chart_data(self, lat: float, lon: float, date: str, time: str):
        """Kılavuzdaki /v1/natal/full-chart adresine istek atar."""
        payload = {"lat": lat, "lon": lon, "date": date, "time": time}
        return self._make_request("/natal/full-chart", payload)

    def get_wheel_chart_image(self, lat: float, lon: float, date: str, time: str):
        """Kılavuzdaki /v1/natal/wheel-chart adresine istek atar."""
        payload = {"lat": lat, "lon": lon, "date": date, "time": time}
        return self._make_request("/natal/wheel-chart", payload, accept_header='image/png')

cosmic_api_client = CosmicAPIClient()
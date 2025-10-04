import requests
import json

# --- AYARLAR: Lütfen bu iki değişkeni kendi bilgilerinizle güncelleyin ---
# 1. Yeni API'nin tam adresi
API_URL = "https://cosmicapiv1-1.onrender.com/v1/synastry/aspects"

# 2. .env dosyanızda bulunan API anahtarınız
API_KEY = "COSMIC_API_SECRET_KEY_12345" # <-- KENDİ API ANAHTARINIZI BURAYA YAZIN

# --- TEST VERİSİ: Loglardan alınan, hataya neden olan örnek bir veri ---
test_payload = {
  "person1": {
    "lat": 37.0628317,
    "lon": 37.3792617,
    "date": "2000-01-05",
    "time": "16:25"
  },
  "person2": {
    "lat": 37.0628317,
    "lon": 37.3792617,
    "date": "2000-01-11",
    "time": "22:20"
  }
}

# --- İSTEK GÖNDERME KISMI ---
def test_synastry_endpoint():
    """
    Cosmic API'nin synastry endpoint'ine tek bir istek gönderir ve sonucu yazdırır.
    """
    print(f"İstek gönderiliyor: {API_URL}")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY  # Yetkilendirme için API anahtarı
    }

    try:
        # requests.post() ile POST isteği gönderiyoruz
        response = requests.post(
            API_URL, 
            headers=headers, 
            data=json.dumps(test_payload), # Veriyi JSON formatında gönderiyoruz
            timeout=90 # 90 saniye içinde yanıt gelmezse hata ver
        )

        # --- SONUÇLARI ANALİZ ETME ---
        print("\n--- İSTEK SONUCU ---")
        print(f"Durum Kodu (Status Code): {response.status_code}")
        print(f"Yanıt Başlıkları (Response Headers): {response.headers}")
        
        # Yanıtın içeriğini yazdırmadan önce kontrol edelim
        if response.text:
            print(f"Yanıt İçeriği (Response Body):\n{response.text}")
        else:
            print("Yanıt İçeriği (Response Body): Boş")

    except requests.exceptions.RequestException as e:
        print("\n--- HATA ---")
        print(f"İstek gönderilirken bir hata oluştu: {e}")

# Script'i çalıştır
if __name__ == "__main__":
    test_synastry_endpoint()
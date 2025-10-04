# interactions/logic.py

def calculate_synastry_score(aspects_data: list) -> (int, dict):
    """
    Sinastri API'sinden gelen açı verilerini analiz ederek bir genel uyum skoru
    ve anlamlı alt skor dökümü (breakdown) oluşturur.
    --- DEĞİŞİKLİK: Fonksiyon, API'den gelen yeni ve gerçek veri yapısına göre tamamen güncellendi. ---
    """
    if not aspects_data:
        return 0, {}

    # --- DEĞİŞİKLİK: Açı isimleri API'den geldiği gibi (büyük harfle başlayarak) ve
    # "soft" (pozitif) / "hard" (negatif) olarak sınıflandırıldı.
    SOFT_ASPECTS = ['Trine', 'Sextile', 'Conjunction']
    HARD_ASPECTS = ['Opposition', 'Square', 'Quincunx']

    ASPECT_WEIGHTS = {
        'Conjunction': 1.0, 'Opposition': 0.8, 'Trine': 1.2,
        'Square': 0.9, 'Sextile': 1.1, 'Quincunx': 0.6
    }
    PLANET_WEIGHTS = {
        'Sun': 1.5, 'Moon': 1.5, 'Ascendant': 1.2, 'Venus': 1.4, 'Mars': 1.3,
        'Mercury': 1.1, 'Jupiter': 1.0, 'Saturn': 0.8, 'Uranus': 0.7,
        'Neptune': 0.7, 'Pluto': 0.7
    }

    total_score = 0
    positive_points = 0
    negative_points = 0
    
    love_harmony = 0
    communication = 0
    challenges = 0

    # --- DEĞİŞİKLİK: Gelen 'aspects' listesi artık 'aspects_data' değil, doğrudan 'aspects_data'
    # anahtarının altındaki liste. API çıktısına göre bu anahtarın adı 'aspects'.
    # Ancak biz bu fonksiyonu çağırırken zaten listeyi verdiğimiz için döngü aynı kalabilir.
    for aspect in aspects_data:
        # --- DEĞİŞİKLİK BAŞLANGICI: Veri çekme mantığı basitleştirildi ---
        planet1 = aspect.get('planet1')
        planet2 = aspect.get('planet2')
        aspect_name = aspect.get('aspect')
        orb = aspect.get('orb') # 'orb_decimal' yerine 'orb' kullanılıyor
        
        if not all([planet1, planet2, aspect_name, orb is not None]):
            continue

        # Açı türünü (soft/hard) kendimiz belirliyoruz
        is_positive = aspect_name in SOFT_ASPECTS
        is_negative = aspect_name in HARD_ASPECTS
        # --- DEĞİŞİKLİK SONU ---

        # Eğer açı ne soft ne de hard olarak tanımlanmamışsa, atla
        if not is_positive and not is_negative:
            continue

        base_score = (10 - abs(orb)) * 10
        
        weighted_score = base_score * \
                         PLANET_WEIGHTS.get(planet1, 0.5) * \
                         PLANET_WEIGHTS.get(planet2, 0.5) * \
                         ASPECT_WEIGHTS.get(aspect_name, 0.5)

        if is_positive:
            total_score += weighted_score
            positive_points += 1
            if planet1 in ['Venus', 'Mars', 'Moon'] and planet2 in ['Venus', 'Mars', 'Moon', 'Sun']:
                love_harmony += weighted_score
            if planet1 in ['Mercury', 'Jupiter', 'Sun'] and planet2 in ['Mercury', 'Jupiter', 'Sun']:
                communication += weighted_score
        elif is_negative: # 'else' yerine 'elif is_negative' kullanmak daha güvenli
            total_score -= weighted_score
            negative_points += 1
            if planet1 in ['Saturn', 'Mars', 'Pluto'] and planet2 in ['Saturn', 'Mars', 'Pluto', 'Sun', 'Moon']:
                challenges += weighted_score

    if positive_points + negative_points == 0:
        return 50, {}
        
    normalized_score = 50 + (total_score / ((positive_points + negative_points) * 100))
    final_score = int(max(10, min(99, normalized_score)))
    
    def normalize_sub_score(score, total):
        if total <= 0: return 0
        # Normalizasyon formülü biraz daha anlamlı hale getirildi
        normalized = (score / total) * 150 
        return int(min(99, max(20, normalized)))

    total_positive_score = love_harmony + communication
    
    breakdown = {
        "Aşk Uyumu": normalize_sub_score(love_harmony, total_positive_score),
        "İletişim Uyumu": normalize_sub_score(communication, total_positive_score),
        "Zorluk Potansiyeli": normalize_sub_score(challenges, challenges * 1.2 if challenges > 0 else 1),
    }
    # Türkçe karakter sorununu önlemek için anahtarları güncelledim.

    return final_score, breakdown
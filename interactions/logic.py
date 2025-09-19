# Lütfen bu kodu kopyalayıp interactions/logic.py dosyasının içine yapıştırın.

def calculate_synastry_score(aspects_data: list) -> (int, dict):
    """
    Sinastri API'sinden gelen açı verilerini analiz ederek bir genel uyum skoru
    ve anlamlı alt skor dökümü (breakdown) oluşturur.

    Args:
        aspects_data: /v1/synastry/aspects endpoint'inden dönen JSON listesi.

    Returns:
        Bir tuple döner: (genel_skor, breakdown_dict)
    """
    if not aspects_data:
        return 0, {}

    # Her açının önemine göre ağırlıklar ve puanlar tanımlayalım
    # Bu değerler, istenen sonuca göre ayarlanabilir (tuning).
    ASPECT_WEIGHTS = {
        'conjunction': 1.0, 'opposition': 0.8, 'trine': 1.2,
        'square': 0.9, 'sextile': 1.1, 'quincunx': 0.6
    }
    PLANET_WEIGHTS = {
        'Sun': 1.5, 'Moon': 1.5, 'Ascendant': 1.2, 'Venus': 1.4, 'Mars': 1.3,
        'Mercury': 1.1, 'Jupiter': 1.0, 'Saturn': 0.8, 'Uranus': 0.7,
        'Neptune': 0.7, 'Pluto': 0.7
    }

    total_score = 0
    positive_points = 0
    negative_points = 0
    
    # Alt skorlar için sayaçlar
    love_harmony = 0       # Venüs, Mars, Ay arasındaki uyumlu açılar
    communication = 0      # Merkür, Güneş, Jüpiter arasındaki uyumlu açılar
    challenges = 0         # Satürn, Mars, Pluto arasındaki zorlayıcı açılar

    for aspect in aspects_data:
        planet1 = aspect.get('planet1', {}).get('name')
        planet2 = aspect.get('planet2', {}).get('name')
        aspect_name = aspect.get('aspect', {}).get('name')
        orb = aspect.get('orb_decimal')
        is_positive = aspect.get('aspect', {}).get('type') == 'soft'
        
        if not all([planet1, planet2, aspect_name, orb is not None]):
            continue

        # Temel puanı hesapla (açı ne kadar darsa o kadar güçlü)
        base_score = (10 - abs(orb)) * 10
        
        # Gezegen ve açı ağırlıklarını uygula
        weighted_score = base_score * \
                         PLANET_WEIGHTS.get(planet1, 0.5) * \
                         PLANET_WEIGHTS.get(planet2, 0.5) * \
                         ASPECT_WEIGHTS.get(aspect_name, 0.5)

        if is_positive:
            total_score += weighted_score
            positive_points += 1
            # Alt skorları doldur
            if planet1 in ['Venus', 'Mars', 'Moon'] and planet2 in ['Venus', 'Mars', 'Moon', 'Sun']:
                love_harmony += weighted_score
            if planet1 in ['Mercury', 'Jupiter', 'Sun'] and planet2 in ['Mercury', 'Jupiter', 'Sun']:
                communication += weighted_score
        else:
            total_score -= weighted_score
            negative_points += 1
            if planet1 in ['Saturn', 'Mars', 'Pluto'] and planet2 in ['Saturn', 'Mars', 'Pluto', 'Sun', 'Moon']:
                challenges += weighted_score

    # Toplam skoru 0-100 aralığına normalize et
    # Bu formül, deneme yanılma ile daha iyi hale getirilebilir
    if positive_points + negative_points == 0:
        return 50, {}
        
    normalized_score = 50 + (total_score / ((positive_points + negative_points) * 100))
    final_score = int(max(10, min(99, normalized_score)))
    
    # Alt skorları 0-100 aralığına normalize et
    # Bu basit bir normalizasyon, daha karmaşık hale getirilebilir
    def normalize_sub_score(score, total):
        if total == 0: return 0
        return int(min(99, (score / total) * 100 * 5))

    total_positive_score = love_harmony + communication
    
    breakdown = {
        "ask_uyumu": normalize_sub_score(love_harmony, total_positive_score),
        "iletisim_uyumu": normalize_sub_score(communication, total_positive_score),
        "zorluk_potansiyeli": normalize_sub_score(challenges, challenges if challenges > 0 else 1),
    }

    return final_score, breakdown
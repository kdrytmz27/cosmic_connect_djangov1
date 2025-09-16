# interactions/logic.py

ELEMENT_MAP = {
    'Aries': 'Fire', 'Leo': 'Fire', 'Sagittarius': 'Fire',
    'Taurus': 'Earth', 'Virgo': 'Earth', 'Capricorn': 'Earth',
    'Gemini': 'Air', 'Libra': 'Air', 'Aquarius': 'Air',
    'Cancer': 'Water', 'Scorpio': 'Water', 'Pisces': 'Water',
}
MODALITY_MAP = {
    'Aries': 'Cardinal', 'Cancer': 'Cardinal', 'Libra': 'Cardinal', 'Capricorn': 'Cardinal',
    'Taurus': 'Fixed', 'Leo': 'Fixed', 'Scorpio': 'Fixed', 'Aquarius': 'Fixed',
    'Gemini': 'Mutable', 'Virgo': 'Mutable', 'Sagittarius': 'Mutable', 'Pisces': 'Mutable',
}
ELEMENT_SCORES = {
    ('Air', 'Fire'): 95, ('Earth', 'Water'): 90, ('Fire', 'Fire'): 85, ('Earth', 'Earth'): 85,
    ('Water', 'Water'): 85, ('Air', 'Air'): 80, ('Earth', 'Fire'): 40, ('Air', 'Water'): 60,
    ('Fire', 'Water'): 30, ('Air', 'Earth'): 35,
}
MODALITY_SCORES = {
    ('Cardinal', 'Cardinal'): 70, ('Fixed', 'Fixed'): 60, ('Mutable', 'Mutable'): 80,
    ('Cardinal', 'Fixed'): 75, ('Fixed', 'Mutable'): 75, ('Cardinal', 'Mutable'): 75,
}

def _get_element_score(sign1, sign2):
    if not all([sign1, sign2]): return 30
    element1, element2 = ELEMENT_MAP.get(sign1), ELEMENT_MAP.get(sign2)
    if not all([element1, element2]): return 30
    return ELEMENT_SCORES.get(tuple(sorted((element1, element2))), 50)

def _get_modality_score(sign1, sign2):
    if not all([sign1, sign2]): return 30
    modality1, modality2 = MODALITY_MAP.get(sign1), MODALITY_MAP.get(sign2)
    if not all([modality1, modality2]): return 30
    return MODALITY_SCORES.get(tuple(sorted((modality1, modality2))), 50)

def calculate_compatibility_score(profile1, profile2) -> int:
    p1 = profile1
    p2 = profile2
    if not all([p1.sun_sign, p1.moon_sign, p1.rising_sign, p2.sun_sign, p2.moon_sign, p2.rising_sign]):
        return 0

    score = (
        (_get_element_score(p1.sun_sign, p2.sun_sign) * 0.30) +
        (_get_element_score(p1.moon_sign, p2.moon_sign) * 0.25) +
        (_get_element_score(p1.rising_sign, p2.rising_sign) * 0.20) +
        (_get_modality_score(p1.sun_sign, p2.sun_sign) * 0.10) +
        (_get_modality_score(p1.moon_sign, p2.moon_sign) * 0.08) +
        (_get_modality_score(p1.rising_sign, p2.rising_sign) * 0.07)
    )
    return int(max(10, min(99, score)))
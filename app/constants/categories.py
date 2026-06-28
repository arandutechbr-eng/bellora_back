"""Categorias do marketplace Bellora — espelho do frontend."""

BEAUTY_CATEGORIES = [
    ("cabelo", "Cabelo", "Cortes, coloração, tratamentos e penteados."),
    ("unhas", "Unhas", "Manicure, nail art e alongamento."),
    ("cilios", "Cílios", "Extensão, volume russo e lifting."),
    ("sobrancelhas", "Sobrancelhas", "Design, henna e micropigmentação leve."),
    ("estetica", "Estética", "Limpeza de pele, peeling e harmonização."),
    ("podologia", "Podologia", "Cuidados com os pés e unhas dos pés."),
    ("maquiagem", "Maquiagem", "Social, noiva e editorial."),
    ("massagem", "Massagem", "Relaxante, modeladora e terapêutica."),
    ("terapia-capilar", "Terapia Capilar", "Cronograma capilar e tratamentos."),
    ("depilacao", "Depilação", "Cera, linha e laser."),
    ("micropigmentacao", "Micropigmentação", "Sobrancelhas, lábios e olhos."),
]

CATEGORY_SLUGS = {slug for slug, _, _ in BEAUTY_CATEGORIES}
SLUG_TO_NAME = {slug: name for slug, name, _ in BEAUTY_CATEGORIES}

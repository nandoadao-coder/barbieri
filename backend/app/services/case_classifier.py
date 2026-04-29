NEGATIVE_ANSWERS = {"não", "nao", "no", "n", "nenhum", "nenhuma"}


def classify_case(collected_data: dict) -> str:
    """
    Retorna 'simple' ou 'complex' baseado nos dados coletados.
    Complexo se tiver filhos menores OU bens a partilhar.
    """
    has_children = str(collected_data.get("has_children", "não")).strip().lower()
    has_assets = str(collected_data.get("has_assets", "não")).strip().lower()

    children_positive = not any(has_children.startswith(neg) for neg in NEGATIVE_ANSWERS)
    assets_positive = not any(has_assets.startswith(neg) for neg in NEGATIVE_ANSWERS)

    if children_positive or assets_positive:
        return "complex"
    return "simple"

def normalize_text(text: str) -> str:
    return text.lower().strip()


def percentage(value, maximum):
    if maximum == 0:
        return 0
    return (value / maximum) * 100
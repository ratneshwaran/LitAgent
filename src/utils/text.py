import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^a-zA-Z0-9\-\_\s]", "", value).strip().lower()
    value = re.sub(r"[\s\_]+", "-", value)
    return value[:100]

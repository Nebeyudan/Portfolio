import re
import unicodedata
from html import escape

_slug_cleanup = re.compile(r"[^a-z0-9-]+")

def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip().replace(" ", "-")
    return _slug_cleanup.sub("-", value).strip("-")

def safe_html(s: str) -> str:
    # If you provide raw HTML snippets in data files, you can pass them through.
    # If you provide *text*, this escapes it safely.
    return escape(s)
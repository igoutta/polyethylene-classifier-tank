"""Escritura de archivos de estado."""

import os
import tempfile


def write_atomic(path, text):
    """Escribe `text` en `path` sin dejarlo a medias si se corta la luz."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, suffix=".tmp", delete=False
    ) as tmp:
        tmp.write(text)
    os.replace(tmp.name, path)

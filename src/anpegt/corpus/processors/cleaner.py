"""Text cleaning utilities for corpus ingestion."""

import re
import unicodedata


def clean_text(raw: str) -> str:
    """Normalize unicode (NFC), strip HTML tags, normalize whitespace.

    Parameters
    ----------
    raw:
        The raw text to clean.

    Returns
    -------
    str
        Cleaned text.
    """
    # Normalize unicode to NFC form
    text = unicodedata.normalize("NFC", raw)

    # Strip HTML tags (simple regex approach)
    text = re.sub(r"<[^>]+>", "", text)

    # Normalize line breaks: collapse 3+ newlines into 2
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Normalize horizontal whitespace: collapse runs of spaces/tabs into single space
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces before newlines
    text = re.sub(r" +\n", "\n", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text

import re
import unicodedata


def clean_text(text):
    if not text:
        return ""

    text = unicodedata.normalize(
        "NFKC",
        text,
    )

    text = text.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()
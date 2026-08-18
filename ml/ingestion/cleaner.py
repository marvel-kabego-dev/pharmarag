PATTERNS_BRUIT = [
    "Westferry Circus",
    "Telephone +44",
    "E-mail info@ema",
    "European Medicines Agency",
    "Scarlattilaan",
    "EMA/",
    "EMEA/",
    "EPAR summary",
    "© European",
    "ema.europa.eu",
    "An agency of the European Union",
]


def clean_pages(pages: list[dict]) -> list[dict]:
    cleaned_pages = []

    for page in pages:
        text = page.get("text", "")
        lines = text.splitlines()
        kept_lines = []

        for line in lines:
            if len(line) <= 2:
                continue
            if any(pattern.lower() in line.lower() for pattern in PATTERNS_BRUIT):
                continue
            kept_lines.append(line)

        cleaned_text = "\n".join(kept_lines)

        cleaned_page = dict(page)
        cleaned_page["text"] = cleaned_text
        cleaned_pages.append(cleaned_page)

    return cleaned_pages

import re


def clean_title(title: str, category: str) -> str:
    if not title:
        return title

    keywords_to_remove = {
        "processor": [
            r"\bprocesor\b",
            r"\bCPU\b",
            r"\bBox\b",
            r"\bOEM\b",
            r"\bTray\b",
        ],
        "graphics_card": [
            r"\bkarta graficzna\b",
            r"\bgraphics card\b",
            r"\bGPU\b",
            r"\bVGA\b",
        ],
        "ram": [
            r"\bpamięć\b",
            r"\bpamiec\b",
            r"\bRAM\b",
            r"\bmemory\b",
        ],
        "case": [
            r"\bobudowa\b",
            r"\bcase\b",
            r"\bshell\b",
        ],
        "storage": [
            r"\bdysk\b",
            r"\bSSD\b",
            r"\bHDD\b",
            r"\bNVMe\b",
            r"\bSATA\b",
        ],
        "power_supply": [
            r"\bzasilacz\b",
            r"\bPSU\b",
            r"\bpower supply\b",
        ],
        "motherboard": [
            r"\bpłyta główna\b",
            r"\bplyta glowna\b",
            r"\bmotherboard\b",
            r"\bmobo\b",
        ],
    }

    general_keywords = [
        r"\bnowy\b",
        r"\bnowa\b",
        r"\bnowe\b",
        r"\bużywany\b",
        r"\buzywany\b",
        r"\bużywana\b",
        r"\bfv\b",
        r"\bgwarancja\b",
        r"\bpolecam\b",
        r"\btanio\b",
        r"\bokazja\b",
        r"\bsprzedam\b",
    ]

    cleaned = title

    if category in keywords_to_remove:
        for keyword in keywords_to_remove[category]:
            cleaned = re.sub(keyword, "", cleaned, flags=re.IGNORECASE)

    for keyword in general_keywords:
        cleaned = re.sub(keyword, "", cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = re.sub(r'\s*[-,/|]\s*', ' ', cleaned)
    cleaned = cleaned.strip(' -,/|')

    return cleaned


def is_bundle_offer(title: str,category: str = None) -> bool:
    if not title:
        return False

    bundle_keywords = [
        r'\bzestaw\b',
        r'\bset\b',
        r'\bkomplet\b',
        r'\bbundle\b',
        r'\bpc\s+gaming\b',
        r'\bkomputer\b',
        r'\bzestaw do gier\b',
        r'\bzestaw komputerowy\b',
    ]

    for keyword in bundle_keywords:
        if re.search(keyword, title, flags=re.IGNORECASE):
            return True

    component_keywords = [
        r'\bprocesor\b',
        r'\bcpu\b',
        r'\bkarta graficzna\b',
        r'\bgpu\b',
        r'\bgtx\b',
        r'\brtx\b',
        r'\bpłyta\s+główna\b',
        r'\bplyta\s+glowna\b',
        r'\bmotherboard\b',
        r'\bmobo\b',
        r'\bzasilacz\b',
        r'\bpsu\b',
        r'\bobudowa\b',
        r'\bcase\b',
        r'\bdysk\b',
        r'\bssd\b',
        r'\bhdd\b',
    ]
    if category != "ram":
        component_keywords.extend([
            r'\bpamięć\b',
            r'\bpamiec\b',
            r'\bram\b',
            r'\bddr\d\b',
        ])

    component_count = sum(1 for keyword in component_keywords
                          if re.search(keyword, title, flags=re.IGNORECASE))

    if component_count >= 3:
        return True

    plus_pattern = r'\b(procesor|cpu|gpu|ram|płyta|plyta|dysk|zasilacz|obudowa)\s*\+\s*(procesor|cpu|gpu|ram|płyta|plyta|dysk|zasilacz|obudowa)\b'
    if re.search(plus_pattern, title, flags=re.IGNORECASE):
        return True

    return False
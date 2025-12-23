import re

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "pny",
    "intel", "radeon"
}
CPU_BRANDS = {
    "amd", "intel"
}
MOTHERBOARD_BRANDS = {
    "asus",
    "msi",
    "gigabyte",
    "asrock",
    "biostar",
    "evga",
    "acer",
    "foxconn",
    "supermicro",
    "intel",
    "colorful",
    "nzxt",
    "dfi"
}
CPU_COOLER_BRANDS = {
    "noctua",
    "fractal",
    "evga",
    "chieftec",
    "aerocool",
    "asus",
    "antec",
    "cougar",
    "evercool",
    "gigabyte",
    "msi",
    "be quiet!",
    "cooler master",
    "corsair",
    "deepcool",
    "nzxt",
    "arctic",
    "thermaltake",
    "scythe",
    "cryorig",
    "ekwb",
    "alphacool",
    "id-cooling",
    "silverstone",
    "phanteks",
    "zalman",
    "thermalright"
}

CASE_MODEL = {
    "atx",
    "micro-atx",
    "mini-itx",
    "e-atx",
    "xl-atx",
    "mini-dtx",
    "pico-itx",
    "nano-itx",
    "flex-atx",
    "thin mini-itx",
    "micro-dtx",
    "htpc",
    "cube",
    "tower",
    "mid-tower",
    "full-tower"
}
motherboard_format = [
    "atx",
    "micro-atx",
    "mini-itx"
]

case_format = {
    "full tower", "mid tower", "mini tower", "micro tower"
}
CASE_BRANDS = {
    "corsair", "fractal design", "nzxt", "cooler master", "thermaltake", "be quiet!", "phanteks",
    "lian li", "silverstone", "antec", "deepcool", "bitfenix", "inwin", "rosewill", "zalman", "aerocool"
    , "xigmatek", "chieftec", "sharkoon", "kolink", "msi", "endorfy", "gigabyte", "genesis", "fsp"
    ,"crystal", "cougar"
}

POWER_SUPPLY_BRANDS = {
    "corsair",
    "seasonic",
    "evga",
    "be quiet!",
    "cooler master",
    "chieftec",
    "thermaltake",
    "silverstone",
    "fractal design",
    "msi",
    "asus",
    "gigabyte",
    "antec",
    "fsp",
    "zalman",
    "lc-power",
    "sharkoon",
    "aerocool"
}
RAM_BRANDS = {
    "corsair",
    "g.skill",
    "gskill",
    "kingston",
    "crucial",
    "adata",
    "patriot",
    "teamgroup",
    "hyperx",
    "ballistix",
    "samsung",
    "transcend",
    "goodram",
    "mushkin",
    "pny",
    "apacer",
    "silicon power",
    "lexar"
}
SSD_BRANDS = {
    "samsung",
    "crucial",
    "kingston",
    "wd",
    "western Digital",
    "seagate",
    "corsair",
    "adata",
    "sandisk",
    "intel",
    "patriot",
    "pny",
    "transcend",
    "toshiba",
    "sk hynix",
    "goodram",
    "teamgroup",
    "gigabyte",
    "lexar",
    "apacer"
}
media_types = ["nvme", "sata", "ssd", "solid state drive", "hdd", "m.2"]


def extract_brand_from_cpu(title: str) -> dict:
    lower_title = title.lower()
    brand = next((b for b in CPU_BRANDS if b in lower_title), None)
    model = lower_title.replace(brand, "") if brand else lower_title
    model = model.replace("core", "")
    return {
        "brand": brand,
        "model": model.strip(),
    }


def extract_brand_from_gpu(title: str) -> str:
    return next((b for b in GPU_BRANDS if b in str.lower(title)), None)


def extract_info_from_gpu(title: str) -> dict:
    lower_title = title.lower()
    brand =  next((b for b in GPU_BRANDS if b in str.lower(title)), None)
    model = lower_title.replace(brand, "") if brand else lower_title
    model = model.replace("core", "")
    return {
        "brand": brand,
        "model": model.strip(),
    }


def extract_brand_from_case(title: str) -> dict:
    brand = next((b for b in CASE_BRANDS if b in str.lower(title)), None)
    model = None
    if brand is not None:
        model = title.replace(brand, "") if brand else title.lower()
    return {
        "brand": brand,
        "model": model
    }


def extract_brand_from_ssd(title: str) -> dict:
    title_lower = title.lower()
    brand = None
    brand = next((b for b in SSD_BRANDS if b in str.lower(title)), None)
    model = None
    if brand is not None:
        model = title_lower.replace(brand, "")
        for media in media_types:
            model = model.replace(media.lower(), "")
        model = re.sub(r"\b\d+(\.\d+)?\s?(gb|tb)\b", "", model).strip()
    return {
        "brand": brand,
        # "model": re.sub(r"\s+", " ", model).strip(),
        "model": model
    }


def extract_brand_from_cpu_cooler(title: str) -> dict:
    brand = next((b for b in CPU_COOLER_BRANDS if b in str.lower(title)), None)
    model = None
    if brand is not None:
        model = title.replace(brand.lower(), "").strip()
        return {
        "brand": brand,
        "model": model
    }


def extract_brand_from_ram(title: str) -> dict:
    brand = next((b for b in RAM_BRANDS if b in str.lower(title)), None)
    if brand is not None:
        title = title.replace(brand, "")

        # Usuń typy RAM
        ram_types = ["ddr4", "ddr5", "ddr3"]
        for ram_type in ram_types:
            title = title.replace(  ram_type, "")

        # Usuń prędkości np. 2400, 3200, 3600 itd.
        title = re.sub(r"\b\d{3,4}\b", "", title)

        # Usuń latency np. cl16, cl18
        title = re.sub(r"\bcl\d{1,2}\b", "", title)

        # Usuń pojemność np. 8 gb, 16gb, itd.
        title = re.sub(r"\b\d+\s?gb\b", "", title)

        # Usuń przecinki, myślniki, wielokrotne spacje
        title = re.sub(r"[,-]", " ", title)
        title = re.sub(r"\s+", " ", title).strip()

    return {
        "brand": brand,
        "model": title
    }


def extract_brand_from_power_supply(title: str) -> dict:
    # brand = None
    brand = next((b for b in POWER_SUPPLY_BRANDS if b in str.lower(title)), None)

    model = None
    if brand is not None:
        model = title.replace(brand, "")
        model = re.sub(r"\b\d{3,4}\s?w\b", "", model).strip()

    return {
        "brand": brand,
        "model": model,
    }


def extract_brand_from_motherboard(title: str) -> dict:
    brand = next((b for b in MOTHERBOARD_BRANDS if b in str.lower(title)), None)
    if brand is not None:
        title = title.replace(brand, "").strip()

    return {
        "brand": brand,
        "model": title
    }



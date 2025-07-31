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
    "silicon power"
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
    # model = title
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
            title = title.replace(ram_type, "")

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

#
# def extract_gpu_details(item: str) -> dict:
#     name_lower = item.lower()
#
#     # Brand
#     brand = next((b for b in GPU_BRANDS if b in name_lower), None)
#
#     # Memory Size (e.g., 12GB, 8 GB)
#     mem_match = re.search(r"(\d{1,3})\s?gb", name_lower)
#     memory_size = int(mem_match.group(1)) if mem_match else None
#
#     # GDDR Version
#     gddr_match = re.search(r"gddr\d", name_lower)
#     gddr_version = gddr_match.group(0).upper() if gddr_match else None
#
#     # Power draw
#     power_match = re.search(r"(\d{2,3})\s?w", name_lower)
#     power_draw = int(power_match.group(1)) if power_match else None
#
#     # Model (remove brand and other known strings)
#     name_parts = item.split()
#     model_parts = [
#         part for part in name_parts
#         if part.lower() not in GPU_BRANDS and not re.search(r"(gb|gddr\d|w|stan)", part.lower())
#     ]
#     model = " ".join(model_parts).strip()
#
#     return {
#         "brand": brand,
#         "model": model if model else None,
#         "memory_size": memory_size,
#         "gddr": gddr_version,
#         "power_draw": power_draw,
#     }
#
#
# def extract_cpu_info(name: str) -> dict:
#     """
#     Extracts brand, model, and clock speed from a CPU product name.
#     Returns a dict with keys: brand, model, base_clock.
#     """
#     name_lower = name.lower()
#     brand = None
#     model = None
#
#     # Intel
#     intel_pattern = r"i([3579])\s*[-\s]*\s*(\d{4,5})([a-z]*)"
#     intel_match = re.search(intel_pattern, name_lower)
#     if "intel" in name_lower or intel_match:
#         brand = "intel"
#         if intel_match:
#             tier = intel_match.group(1)
#             model_number = intel_match.group(2)
#             suffix = intel_match.group(3)
#             model = f"i{tier}-{model_number}{suffix}"
#
#     # AMD
#     amd_pattern = r"ryzen\s+([3579])\s+(\d{4})([a-z]*)"
#     amd_match = re.search(amd_pattern, name_lower)
#     if "amd" in name_lower or amd_match:
#         brand = "amd"
#         if amd_match:
#             tier = amd_match.group(1)
#             model_number = amd_match.group(2)
#             suffix = amd_match.group(3)
#             model = f"ryzen {tier} {model_number}{suffix}"
#
#     # Clock speed
#     ghz_pattern = r"(\d+)[,.](\d+)\s*ghz"
#     matches = re.findall(ghz_pattern, name_lower, re.IGNORECASE)
#     base_clock = None
#     if matches:
#         speeds = [float(f"{m[0]}.{m[1]}") for m in matches]
#         base_clock = f"{min(speeds):.1f}GHz"
#
#     return {
#         "brand": brand,
#         "model": model,
#         "base_clock": base_clock
#     }
#
#
# def extract_case_info(name: str) -> dict:
#     name_lower = name.lower()
#     brand = next((b for b in CASE_BRANDS if b in name_lower), None)
#     # Format (e.g. full tower, mid tower, etc.)
#     format_match = next((f for f in case_format if f in name_lower), None)
#     return {
#         "brand": brand,
#         "format": format_match
#     }
#
#
# def extract_ram_info(name: str) -> dict:
#     name_lower = name.lower()
#     ram_info = {}
#     brand = next((b for b in RAM_BRANDS if b in name_lower), None)
#     # RAM capacity
#     capacity_match = re.search(r"(\d+)\s*gb", name_lower)
#     ram_info["capacity"] = int(capacity_match.group(1)) if capacity_match else None
#     # RAM type
#     type_match = re.search(r"ddr\d", name_lower)
#     ram_info["type"] = type_match.group(0).upper() if type_match else None
#     # RAM speed
#     speed_match = re.search(r"(\d{3,4})\s*mhz", name_lower)
#     ram_info["speed"] = f"{speed_match.group(1)}MHz" if speed_match else None
#     # Latency
#     latency_match = re.search(r"cl\d+", name_lower)
#     ram_info["latency"] = latency_match.group(0).upper() if latency_match else None
#     ram_info["brand"] = brand
#     return ram_info
#
#
# def extract_storage_info(name: str) -> dict:
#     name_lower = name.lower()
#     brand = next((b for b in SSD_BRANDS if b in name_lower), None)
#     # Capacity
#     capacity_match = re.search(r"(\d+)\s*gb", name_lower)
#     capacity = int(capacity_match.group(1)) if capacity_match else None
#     return {
#         "brand": brand,
#         "capacity": capacity
#     }
#
#
# def extract_power_supply_info(name: str) -> dict:
#     name_lower = name.lower()
#     brand = next((b for b in POWER_SUPPLY_BRANDS if b in name_lower), None)
#     # Capacity
#     capacity_match = re.search(r"(\d+)\s*w", name_lower)
#     capacity = int(capacity_match.group(1)) if capacity_match else None
#     return {
#         "brand": brand,
#         "capacity": capacity
#     }
#
#
# def extract_motherboard_info(name: str) -> dict:
#     name_lower = name.lower()
#     brand = next((b for b in MOTHERBOARD_BRANDS if b in name_lower), None)  # Many MBs have same brands as cases
#     # Chipset
#     chipset_match = re.search(r"b\d{3,4}", name_lower)
#     chipset = chipset_match.group(0).upper() if chipset_match else None
#     # Socket type
#     socket_match = re.search(r"socket\s*(\w+)", name_lower)
#     socket = socket_match.group(1).upper() if socket_match else None
#     # Memory type
#     memory_match = re.search(r"ddr\d", name_lower)
#     memory = memory_match.group(0).upper() if memory_match else None
#     # Format
#     format_match = next((f for f in motherboard_format if f in name_lower), None)
#     return {
#         "brand": brand,
#         "chipset": chipset,
#         "socket_type": socket,
#         "memory_type": memory,
#         "format": format_match
#     }

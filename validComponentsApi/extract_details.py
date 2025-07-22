import re

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "nvidia"
}
CPU_BRANDS = {
    "amd", "intel"
}

def extract_gpu_details(item: dict) -> dict:
    parsed_gpus = {}
    # for item in gpu_items:
    name_lower = item.lower()

        # Brand
    brand = next((b for b in GPU_BRANDS if b in name_lower), None)

        # Memory Size (e.g., 12GB, 8 GB)
    mem_match = re.search(r"(\d{1,3})\s?gb", name_lower)
    memory_size = int(mem_match.group(1)) if mem_match else None

        # GDDR Version
    gddr_match = re.search(r"gddr\d", name_lower)
    gddr_version = gddr_match.group(0).upper() if gddr_match else None

        # Power draw — trudniejsze, często nie ma, można spróbować z "W"
    power_match = re.search(r"(\d{2,3})\s?w", name_lower)
    power_draw = int(power_match.group(1)) if power_match else None

        # Model (usunę markę i inne znane ciągi, zostanie mniej więcej model)
    name_parts = item["name"].split()
    model_parts = [
            part for part in name_parts
            if part.lower() not in GPU_BRANDS and not re.search(r"(gb|gddr\d|w|stan)", part.lower())
        ]
    model = " ".join(model_parts).strip()

    parsed_gpus.append({
            "brand": brand,
            "model": model if model else None,
            # "condition": item["status"],
            # "photo_url": item["img"],
            # "website_url": item["url"],
            # "price" : item["price"],
            "memory_size": memory_size,
            "gddr": gddr_version,
            "power_draw": power_draw,
        })

    return parsed_gpus

def extract_cpu_info(name: str) -> dict:
    """
    Extracts brand, model, and clock speed from a CPU product name.
    Returns a dict with keys: brand, model, base_clock.
    """
    name_lower = name.lower()
    brand = None
    model = None

    # Intel
    intel_pattern = r"i([3579])\s*[-\s]*\s*(\d{4,5})([a-z]*)"
    intel_match = re.search(intel_pattern, name_lower)
    if "intel" in name_lower or intel_match:
        brand = "intel"
        if intel_match:
            tier = intel_match.group(1)
            model_number = intel_match.group(2)
            suffix = intel_match.group(3)
            model = f"i{tier}-{model_number}{suffix}"

    # AMD
    amd_pattern = r"ryzen\s+([3579])\s+(\d{4})([a-z]*)"
    amd_match = re.search(amd_pattern, name_lower)
    if "amd" in name_lower or amd_match:
        brand = "amd"
        if amd_match:
            tier = amd_match.group(1)
            model_number = amd_match.group(2)
            suffix = amd_match.group(3)
            model = f"ryzen {tier} {model_number}{suffix}"

    # Clock speed
    ghz_pattern = r"(\d+)[,.](\d+)\s*ghz"
    matches = re.findall(ghz_pattern, name_lower, re.IGNORECASE)
    base_clock = None
    if matches:
        speeds = [float(f"{m[0]}.{m[1]}") for m in matches]
        base_clock = f"{min(speeds):.1f}GHz"

    return {
        "brand": brand,
        "model": model,
        "base_clock": base_clock
    }
import re

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "nvidia"
}


def extract_gpu_details(gpu_items: list[dict]) -> list[dict]:
    parsed_gpus = []
    for item in gpu_items:
        name_lower = item["name"].lower()

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
            "condition": item["status"],
            "photo_url": item["img"],
            "website_url": item["url"],
            "price" : item["price"],
            "memory_size": memory_size,
            "gddr": gddr_version,
            "power_draw": power_draw,
        })

    return parsed_gpus

import re

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "nvidia"
}
CPU_BRANDS = {
    "amd", "intel"
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

def extract_intel_model(name_lower: str) -> str | None:
    """
    Extract Intel CPU model from product name.
    
    Args:
        name_lower: Lowercase product name string
    
    Returns:
        Normalized Intel model string or None if not found
    """
    # Regex pattern to match Intel CPU models
    # Matches: i3, i5, i7, i9 followed by optional hyphen/spaces and generation/model number
    # Also captures optional suffixes like F, K, KF, T, etc.
    intel_pattern = r"i([3579])\s*[-\s]*\s*(\d{4,5})([a-z]*)"
    
    match = re.search(intel_pattern, name_lower)
    if match:
        tier = match.group(1)  # 3, 5, 7, or 9
        model_number = match.group(2)  # e.g., 6400, 14400
        suffix = match.group(3)  # e.g., f, k, kf, t
        
        # Normalize format to lowercase with hyphen
        model = f"i{tier}-{model_number}{suffix}"
        return model
    
    return None

def extract_amd_model(name_lower: str) -> str | None:
    """
    Extract AMD CPU model from product name.
    
    Args:
        name_lower: Lowercase product name string
    
    Returns:
        Normalized AMD model string or None if not found
    """
    # Regex pattern to match AMD Ryzen models
    # Matches: ryzen followed by tier (3, 5, 7, 9) and model number with optional suffix
    # Examples: "ryzen 5 5600x", "ryzen 9 5900x", "ryzen 7 3700x"
    amd_pattern = r"ryzen\s+([3579])\s+(\d{4})([a-z]*)"
    
    match = re.search(amd_pattern, name_lower)
    if match:
        tier = match.group(1)  # 3, 5, 7, or 9
        model_number = match.group(2)  # e.g., 5600, 5900, 3700
        suffix = match.group(3)  # e.g., x, xt, g, etc.
        
        # Normalize format to lowercase with spaces
        model = f"ryzen {tier} {model_number}{suffix}"
        return model
    
    return None

def extract_clock_speed(name_lower: str) -> str | None:
    """
    Extract base clock speed from product name.
    
    Args:
        name_lower: Lowercase product name string
    
    Returns:
        Normalized clock speed string (e.g., "4.6GHz") or None if not found
    """
    # Regex pattern to match GHz values in various formats
    # Matches patterns like: "4.6 GHz", "4.6GHz", "2,5 GHz" (European format), "4,6GHz"
    # Also handles optional spaces and case variations
    ghz_pattern = r"(\d+)[,.](\d+)\s*ghz"
    
    # Find all GHz matches in the string (case-insensitive)
    matches = re.findall(ghz_pattern, name_lower, re.IGNORECASE)
    
    if matches:
        # Convert European decimal format (comma) to standard format (dot)
        # When multiple speeds are present, typically the first/lower one is base clock
        # Sort to get the lowest value as base clock
        speeds = []
        for match in matches:
            whole_part = match[0]
            decimal_part = match[1]
            speed_value = float(f"{whole_part}.{decimal_part}")
            speeds.append(speed_value)
        
        if speeds:
            # Get the base clock (typically the lower value when multiple are present)
            base_speed = min(speeds)
            # Format to one decimal place and normalize to "X.XGHz" format
            return f"{base_speed:.1f}GHz"
    
    return None

def extract_cpu_details(cpu_items: list[dict]) -> list[dict]:
    """
    Extract CPU details from scraped product data.
    
    Args:
        cpu_items: List of dictionaries containing scraped CPU data
                  Each dict should have keys: name, status, img, url, price
    
    Returns:
        List of dictionaries with extracted CPU details
        Each dict contains: brand, model, base_clock, condition, photo_url, website_url, price
    """
    parsed_cpus = []
    for item in cpu_items:
        name_lower = item["name"].lower()
        
        # Brand detection logic - case-insensitive matching
        brand = None
        if "intel" in name_lower:
            brand = "intel"
        elif "amd" in name_lower:
            brand = "amd"
        
        # Model extraction logic
        model = None
        if brand == "intel":
            model = extract_intel_model(name_lower)
        elif brand == "amd":
            model = extract_amd_model(name_lower)
        
        # Clock speed extraction logic
        base_clock = extract_clock_speed(name_lower)

        parsed_cpus.append({
            "brand": brand,
            "model": model,
            "base_clock": base_clock,
            "condition": item["status"],
            "photo_url": item["img"],
            "website_url": item["url"],
            "price": item["price"]
        })

    return parsed_cpus
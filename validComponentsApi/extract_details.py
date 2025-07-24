import re

GPU_BRANDS = {
    "asus", "msi", "gigabyte", "zotac", "evga", "palit", "gainward", "xfx", "powercolor", "sapphire", "inno3d", "nvidia"
}
CPU_BRANDS = {
    "amd", "intel"
}
CASE_MODEL ={
    "micro"
}
motherboard_format = {
    "atx", "micro-atx", "mini-itx"
    }

case_format = {
    "full tower", "mid tower", "mini tower", "micro tower"
    }

def extract_gpu_details(item: str) -> dict:
    name_lower = item.lower()

    # Brand
    brand = next((b for b in GPU_BRANDS if b in name_lower), None)

    # Memory Size (e.g., 12GB, 8 GB)
    mem_match = re.search(r"(\d{1,3})\s?gb", name_lower)
    memory_size = int(mem_match.group(1)) if mem_match else None

    # GDDR Version
    gddr_match = re.search(r"gddr\d", name_lower)
    gddr_version = gddr_match.group(0).upper() if gddr_match else None

    # Power draw
    power_match = re.search(r"(\d{2,3})\s?w", name_lower)
    power_draw = int(power_match.group(1)) if power_match else None

    # Model (remove brand and other known strings)
    name_parts = item.split()
    model_parts = [
        part for part in name_parts
        if part.lower() not in GPU_BRANDS and not re.search(r"(gb|gddr\d|w|stan)", part.lower())
    ]
    model = " ".join(model_parts).strip()

    return {
        "brand": brand,
        "model": model if model else None,
        "memory_size": memory_size,
        "gddr": gddr_version,
        "power_draw": power_draw,
    }


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


def extract_case_info(name: str) -> dict:

    #format(full tower, mini tower, micro tower)
    format_match = re.search(r"(\w+\s*\w+)", name, re.IGNORECASE)
    if format_match:
        case_format = format_match.group(1).lower()
    else:
        case_format = None
    
    return {
        "format": case_format
    }

def extract_ram_info(name: str) -> dict:
    ram_info = {}

    # RAM capacity
    capacity_match = re.search(r"(\d+)\s*gb", name, re.IGNORECASE)
    if capacity_match:
        ram_info["capacity"] = int(capacity_match.group(1))
    else:
        ram_info["capacity"] = None

    # RAM type
    type_match = re.search(r"ddr\d", name, re.IGNORECASE)
    if type_match:
        ram_info["type"] = type_match.group(0).upper()
    else: 
        ram_info["type"] = None
    
    # RAM speed
    speed_match = re.search(r"(\d{3,4})\s*mhz", name, re.IGNORECASE)
    if speed_match:
        ram_info["speed"] = f"{speed_match.group(1)}MHz"
    else:
        ram_info["speed"] = None
    
    # Latency
    latency_match = re.search(r"cl\d+", name, re.IGNORECASE)
    if latency_match:
        ram_info["latency"] = latency_match.group(0).upper()
    else:
        ram_info["latency"] = None

    return ram_info


def extract_storage_info(name: str) -> dict:
    #capacity
    capacity_match = re.search(r"(\d+)\s*gb", name, re.IGNORECASE)
    if capacity_match:
        capacity = int(capacity_match.group(1))
    else:
        capacity = None
    
    return {
        "capacity": capacity
    }

def extract_power_supply_info(name: str) -> dict:
    #capacity
    capacity_match = re.search(r"(\d+)\s*w", name, re.IGNORECASE)
    if capacity_match:
        capacity = int(capacity_match.group(1))
    else:
        capacity = None

    return {
        "capacity": capacity
    }

def extract_motherboard_info(name: str) -> dict:
    # Chipset
    chipset_match = re.search(r"b\d{3,4}", name, re.IGNORECASE)
    if chipset_match:
        chipset = chipset_match.group(0).upper()
    else:
        chipset = None
    
    # Socket type
    socket_match = re.search(r"socket\s*(\w+)", name, re.IGNORECASE)
    if socket_match:
        socket = socket_match.group(1).upper()
    else:
        socket = None
    
    # Memory type
    memory_match = re.search(r"ddr\d", name, re.IGNORECASE)
    if memory_match:
        memory = memory_match.group(0).upper()
    else:
        memory = None

    # Format
    format_match = re.search(r"atx|micro-atx|mini-itx", name, re.IGNORECASE)
    if format_match:
        form_factor = format_match.group(0).upper()
    else:
        form_factor = None
        
    return {
        "chipset": chipset,
        "socket": socket,
        "memory_type": memory,
        "form_factor": form_factor
    }
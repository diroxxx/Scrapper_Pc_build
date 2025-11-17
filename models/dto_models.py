from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


class ComponentType(Enum):
    """Enum reprezentujący typy komponentów - zgodny z backendem Java"""
    GRAPHICS_CARD = "graphics_card"
    PROCESSOR = "processor"
    MEMORY = "ram"
    MOTHERBOARD = "motherboard"
    POWER_SUPPLY = "power_supply"
    STORAGE = "storage"
    CASE_PC = "case"
    CPU_COOLER = "cpu_cooler"

    def to_java_enum(self) -> str:
        """Konwertuje na wartość zgodną z Java enum"""
        java_mapping = {
            ComponentType.GRAPHICS_CARD: "GRAPHICS_CARD",
            ComponentType.PROCESSOR: "PROCESSOR",
            ComponentType.MEMORY: "MEMORY",
            ComponentType.MOTHERBOARD: "MOTHERBOARD",
            ComponentType.POWER_SUPPLY: "POWER_SUPPLY",
            ComponentType.STORAGE: "STORAGE",
            ComponentType.CASE_PC: "CASE_PC",
            ComponentType.CPU_COOLER: "CPU_COOLER",
        }
        return java_mapping[self]


# Mapowanie stringów na enum
CATEGORY_MAPPING = {
    "graphics_card": ComponentType.GRAPHICS_CARD,
    "processor": ComponentType.PROCESSOR,
    "ram": ComponentType.MEMORY,
    "memory": ComponentType.MEMORY,
    "motherboard": ComponentType.MOTHERBOARD,
    "power_supply": ComponentType.POWER_SUPPLY,
    "storage": ComponentType.STORAGE,
    "case": ComponentType.CASE_PC,
    "cpu_cooler": ComponentType.CPU_COOLER,
}


@dataclass
class ComponentOfferDto:
    """Model reprezentujący pojedynczą ofertę komponentu"""
    title: str
    brand: str
    category: str  # Python używa stringa, konwertujemy do enum
    img: str
    model: str
    price: float
    shop: str
    status: str
    url: str

    def to_dict(self) -> Dict[str, Any]:
        """Konwertuje do dict z kategorią jako Java enum"""
        data = asdict(self)
        
        # Konwertuj category na wartość enum dla Javy
        category_enum = CATEGORY_MAPPING.get(self.category.lower())
        if category_enum:
            data['category'] = category_enum.to_java_enum()
        else:
            # Fallback - pozostaw oryginalną wartość
            print(f"Warning: Unknown category '{self.category}', using as-is")
            data['category'] = self.category
        
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentOfferDto':
        return cls(**data)


@dataclass
class ScrapingOfferDto:
    """Model reprezentujący wynik scrapowania dla jednego sklepu"""
    updateId: int
    shopName: str
    componentsData: List[ComponentOfferDto]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "updateId": self.updateId,
            "shopName": self.shopName,
            "componentsData": [comp.to_dict() for comp in self.componentsData]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrapingOfferDto':
        components = [
            ComponentOfferDto.from_dict(comp) if isinstance(comp, dict) else comp
            for comp in data.get("componentsData", [])
        ]
        return cls(
            updateId=data["updateId"],
            shopName=data["shopName"],
            componentsData=components
        )
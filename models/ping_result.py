from dataclasses import dataclass
from typing import Optional

@dataclass
class PingResult:
    ip: str
    node_name: str
    delay: str
    address: Optional[str] = "未知"

    @property
    def delay_float(self) -> float:
        """将延迟转换为浮点数用于排序"""
        return float(self.delay) if self.delay.isdigit() else float('inf')

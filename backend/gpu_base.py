from dataclasses import dataclass, asdict
from typing import Optional
import time

@dataclass
class GPUmetrics:
    gpu_name: str
    gpu_util: float
    mem_util: float
    mem_used_mb: int
    mem_total_mb: int
    temperature: float
    power_draw: float
    power_limit: float
    throttle_reason: str
    timestamp: float

    @property
    def mem_pct(self) -> float:
        if self.mem_total_mb == 0:
            return 0.0
        return round(self.mem_used_mb / self.mem_total_mb * 100, 1)

    @property
    def power_pct(self) -> float:
        if self.power_limit <= 0:
            return 0.0
        return round(self.power_draw / self.power_limit * 100, 1)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["mem_pct"] = self.mem_pct
        d["power_pct"] = self.power_pct
        return d


THROTTLE_CODE_MAP = {
    "0x0000000000000000": "none",
    "0x0000000000000001": "none",
    "0x0000000000000008": "power_limit",
    "0x0000000000000020": "thermal",
    "0x0000000000000040": "sync_boost",
    "0x0000000000000080": "board_limit",
}


def parse_throttle(code: str) -> str:
    code = code.strip().lower()
    return THROTTLE_CODE_MAP.get(code, "unknown")


def mock() -> GPUmetrics:
    t = time.time()
    cycle = (t % 60) / 60
    util = max(0, min(100, 20 + 60 * abs(0.5 - cycle) * 2))
    mem = int(1800 + 1800 * cycle)
    temp = 55 + 25 * cycle
    throttle = "thermal" if temp > 75 else "none"
    return GPUmetrics(
        gpu_name="Mock GPU",
        gpu_util=round(util, 1),
        mem_util=round(util * 0.8, 1),
        mem_used_mb=mem,
        mem_total_mb=4096,
        temperature=round(temp, 1),
        power_draw=round(25 + 55 * cycle, 1),
        power_limit=80.0,
        throttle_reason=throttle,
        timestamp=t,
    )

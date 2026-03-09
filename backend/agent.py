from typing import Optional
import json
from gpu_m import GPUmetrics
import time

class WatcherAgent:
    def __init__(self):
        self.mode=None
        self.last_diagnosis:Optional[dict]=None
        self.history:list[dict]=[]

    @staticmethod
    def rule_based(m: GPUmetrics) -> dict:
        if m.throttle_reason == "thermal" or m.temperature > 85:
            return {
                "status": "critical",
                "headline": "GPU is thermal throttling—performance reduced.",
                "diagnosis": (
                    f"Your GPU is at {m.temperature}°C and has hit its thermal limit. "
                    "The driver is cutting clock speeds to protect the hardware. "
                    "This directly reduces frame rates and compute throughput."
                ),
                "action": "Improve case airflow, clean dust filters, or reduce the GPU power limit by 10-15%.",
                "bottleneck": "thermal_throttle",
            }
        if m.mem_pct > 90:
            return {
                "status": "critical",
                "headline": f"VRAM nearly full ({m.mem_pct}%)—expect stutters.",
                "diagnosis": (
                    f"Only {m.mem_total_mb - m.mem_used_mb} MB of VRAM remains. "
                    "The GPU must evict data to system RAM, causing severe stalls. "
                    "This is the primary source of stuttering or OOM crashes."
                ),
                "action": (
                    "Lower texture quality / resolution, reduce batch size, "
                    "or enable gradient checkpointing (ML)."
                ),
                "bottleneck": "vram_bound",
            }
        if m.power_pct > 95 and m.power_limit > 0:
            return {
                "status": "warning",
                "headline": "GPU hitting power limit—clocks may be reduced.",
                "diagnosis": (
                    f"Power draw is {m.power_draw}W vs limit {m.power_limit}W ({m.power_pct}%). "
                    "The driver is throttling clocks to stay within the power envelope. "
                    "Performance is slightly below its potential."
                ),
                "action": "Raise the power limit in nvidia-settings, or reduce workload intensity.",
                "bottleneck": "power_throttle",
            }
        if m.gpu_util < 20:
            return {
                "status": "warning",
                "headline": "GPU is mostly idle—CPU or I/O is the bottleneck.",
                "diagnosis": (
                    f"GPU utilization is only {m.gpu_util}%. The workload is not keeping the GPU fed. "
                    "For ML: increase DataLoader workers / prefetch factor. "
                    "For video: check hardware acceleration is enabled."
                ),
                "action": "Increase DataLoader num_workers, enable hardware encoding, or check CPU bottleneck.",
                "bottleneck": "gpu_idle",
            }
        if m.gpu_util > 90:
            return {
                "status": "healthy",
                "headline": "GPU is fully compute-bound—running at peak.",
                "diagnosis": (
                    f"Utilization is {m.gpu_util}% with temps at {m.temperature}°C. "
                    "The GPU is the bottleneck, which is ideal for throughput. "
                    "No immediate action needed."
                ),
                "action": "Nothing required—GPU is performing optimally.",
                "bottleneck": "compute_bound",
            }
        return {
            "status": "healthy",
            "headline": "GPU health looks normal.",
            "diagnosis": (
                f"Utilization {m.gpu_util}%, VRAM {m.mem_pct}%, temp {m.temperature}°C. "
                "All metrics are within healthy ranges. No bottleneck detected."
            ),
            "action": "Keep monitoring—no action needed.",
            "bottleneck": "none",
        }
agent=WatcherAgent()
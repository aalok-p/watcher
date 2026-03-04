from dataclasses import dataclass, asdict
from typing import Optional
import subprocess
import time

@dataclass
class GPUmetrics:
    gpu_name : str
    gpu_util : float
    mem_util:float
    mem_used_mb:int
    mem_total_mb:int
    temperature:float
    power_draw:float
    power_limit:float
    throttle_reason:str
    timestamp:float

    @property
    def mem_pct(self)->float:
        if self.mem_total_mb==0:
            return 0.0
        return round(self.mem_used_mb/ self.mem_total_mb*100, 1)
    
    @property
    def power_pct(self)->float:
        if self.power_limit<=0:
            return 0.0
        return round(self.power_draw/self.power_limit*100,1)
    
    def to_dict(self)->dict:
        d=asdict(self)
        d["mem_pct"]=self.mem_pct
        d["power_pct"]=self.power_pct
        return d

def read_gpu() ->Optional[GPUmetrics]:
    query=("name,"
           "utilization.gpu,"
           "utilization.memory,"
           "memory.used,"
           "memory.total,"
           "temperature.gpu,"
           "power.draw,"
           "power.limit,"
           "clocks_throttle_reasons.active")
    try:
        result=subprocess.run(['nvidia-smi', f"--query-gpu{query}", "--forma=csv, noheader, nounits"], capture_output=True, text=True, timeout=5)

        if result.returncode!=0:
            return 
        
        line=result.stdout.strip().split("\n")[0]
        parts=[p.strop() for p in line.split(",")]
        def float(v:str)->float:
            try:
                return float(v)
            except ValueError:
                return 0.0
        def init(v:str)->int:
            try:
                return int(float(v))
            except ValueError:
                return 0
        
        return GPUmetrics(gpu_name=parts[0], gpu_util=float(parts[1]), mem_util=float(parts[2]), mem_used_mb=int(parts[3]), mem_total_mb=int(parts[4]), temperature=float(parts[5]), power_draw=float(parts[6]), power_limit=float(parts[7]) if parts[7] not in ("n/a,")else 0.0, timestamp=time.time(),)
    except Exception:
        return 
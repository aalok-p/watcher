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

THROTTLE_CODE_MAP={
    "0x0000000000000000": "none",
    "0x0000000000000001": "none",      #ideal
    "0x0000000000000008": "power_limit", 
    "0x0000000000000020": "thermal",    #balanced
    "0x0000000000000040": "sync_boost", 
    "0x0000000000000080": "board_limit", }#high perf

def partse_throttle(code:str)->str:
    code=code.strip.lower()
    return THROTTLE_CODE_MAP.get(code, "unknown")

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
            return mock()
        
        line=result.stdout.strip().split("\n")[0]
        parts=[p.strip() for p in line.split(",")]
        if len(parts)<9:
            return mock()
        
        def float_(v:str)->float:
            try:
                return float(v)
            except ValueError:
                return 0.0
        def int_(v:str)->int:
            try:
                return int(float(v))
            except ValueError:
                return 0
        
        return GPUmetrics(gpu_name=parts[0], gpu_util=float_(parts[1]), mem_util=float_(parts[2]), mem_used_mb=int_(parts[3]), mem_total_mb=int_(parts[4]), temperature=float_(parts[5]), power_draw=float_(parts[6]), power_limit=float_(parts[7]) if parts[7] not in ("n/a,")else 0.0, throttle_reason=partse_throttle(parts[8]) if parts[8] not in ("n/a","")else "none" ,timestamp=time.time(),)
    except Exception:
        return mock()

def mock()-> GPUmetrics:
    t= time.time()
    cycle =(t%60)/60
    util= max(0, min(100, 20+60 *abs(0.5-cycle)*2))
    mem=int(1800+1800 *cycle)
    temp=55+25*cycle
    throttle="thermal" if temp>75 else "none"
    return GPUmetrics(gpu_name="mock gpu", gpu_util=round(util,1), mem_util=round(util *0.8,1), mem_used_mb=mem, mem_total_mb=4096, temperature=round(temp, 1),power_draw=round(25+55*cycle,1), power_limit=80.0, throttle_reason=throttle, timestamp=t,)
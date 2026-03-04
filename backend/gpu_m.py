from dataclasses import dataclass, asdict

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
    
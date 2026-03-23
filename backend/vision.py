import os
import io
import logging
import torch
from transfomers import AutoModelForCasualLM, AutoTokenizer


logger = logging.getLogger(__name__)
class Moondream_ai:
    def __init__(self, model_id:str ="vikhyatk/moondream2", cache_dir: Optional[str]=None):
        self.mode=None
        self.tokenizer=None
        self.model_id=model_id
        self,cache_dir=cache_dir
        self.loaded=False

    
    def load_model(self):
        logger.infor(f"loading moondream model: {self.model_id}")

        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)

        self.model = AutoModelForCasualLM.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            cache_dir=self.cache_dir,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else "cpu"
        )
        self.tokenizer= AutoTokenizer.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            cache_dir=self.cache_dir )
        self.loaded=True
        logger.info("moondream model loaded successfully")
    
    def is_ready(self)->bool:
        return self.loaded and self.mode is not None
    
    
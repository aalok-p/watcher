import os
import io
import logging
import torch
from transfomers import AutoModelForCasualLM, AutoTokenizer
from PIL import Image
import base64
from typing import Optional, dict

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
    
    def analyze_image(self, image:Image.Image, question:str)-> Optional[str]:
        if not self.is_ready():
            logger.warining("model not ready")
            return None
        try:
            enc_image = self.model.encode_image(image)
            #ans
            answer =self.model.answer_question(enc_image, question, self.tokenizer)
            return answer.strip()

        except Exception as e:
            logger.error("failed to analyze image: {e}")
            return None
    
    def analyze_base64(self, b64_image:str, question:str)->Optional[str]:
        if not b64_image:
            return None
        try:
            image_data= base64.b64decode(b64_image)
            image = Image.open(io.BytesIO(image_data))

            return self,self.analyze_image(image, question)
        except Exception as e:
            return None
    
    

    
    
import os

class Config:
    LM_STUDIO_URL = os.environ.get('LM_STUDIO_URL') or 'http://localhost:1234'
    SD_URL = os.environ.get('SD_URL') or 'http://localhost:7860'

LM_STUDIO_URL = Config.LM_STUDIO_URL
SD_URL = Config.SD_URL
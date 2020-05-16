import os 

from dotenv import load_dotenv

def init_env():
  ROOT_DIR = os.path.dirname(os.path.abspath(__file__)) 
  load_dotenv(os.path.join(ROOT_DIR, '.env'))

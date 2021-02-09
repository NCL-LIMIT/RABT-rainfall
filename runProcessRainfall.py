from processRainfall import runAPICall
import time
from dotenv import load_dotenv
load_dotenv()

while(True):
    runAPICall(None,None)
    time.sleep(6)

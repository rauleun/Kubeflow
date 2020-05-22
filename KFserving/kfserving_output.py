import json
import numpy as np
import cv2
from PIL import Image

with open("ocr_det_output.json") as f:
    preds = json.loads(f.read())["predictions"]
    preds = np.array(preds) 
    cv2.imwrite('ocr_det_output.png',np.squeeze(preds)) 

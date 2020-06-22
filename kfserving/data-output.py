import json
import numpy as np
import cv2

with open("output.json") as f:
    preds = json.loads(f.read())["predictions"]
    preds = np.array(preds) 
    cv2.imwrite('output.png',np.squeeze(preds)) 

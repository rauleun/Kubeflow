import pickle
import numpy as np
import json
import cv2
from PIL import Image

output_path = 'ocr_det.json'
with open('ocr_det.pkl', 'rb') as ocr_file:
    image = pickle.load(ocr_file)

cv2.imwrite('ocr_det.png',np.squeeze(image))

image = image.tolist()
data = json.dumps({"instances": image})

with open(output_path, 'w') as outfile:
    outfile.write(data)

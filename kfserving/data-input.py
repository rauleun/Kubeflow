import json 
import numpy as np 
import cv2

data_path = "data-espcn/blur2/0100"
image_path = data_path + ".png"
output_path = data_path + ".json"

input_image = cv2.imread(image_path)
input_image = np.expand_dims(input_image, 0)
print(input_image.shape)
print(image_path)
input_json = json.dumps({ "instances": input_image.tolist()})
with open(output_path, 'w') as outfile:
    outfile.write(input_json)

import torch
from application.ml import utils
import numpy as np
import cv2

#############################################
# CUDA for PyTorch
#############################################
use_cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")
torch.backends.cudnn.benchmark = True

#############################################
# CNN settings
#############################################
CLASSES = ["_", "Diffuse", "Mixed", "Dense"]
MODEL_NAME = "genetico.pth"

ModelFit = utils.LoadModel(modelname=MODEL_NAME)


def loadImage(image_bytes):
    img = cv2.cvtColor(image_bytes, cv2.COLOR_BGR2RGB)
    return torch.from_numpy(img.transpose((2, 0, 1)))


def apply_nms(orig_prediction, iou_thresh):
    mask = orig_prediction['scores'] > iou_thresh
    for key, val in orig_prediction.items():
        orig_prediction[key] = val[mask]
    return orig_prediction


def Predict(image_bytes, model):
    Img = loadImage(image_bytes)
    answer = model([Img.float()])[0]
    answer = apply_nms(answer, 0.7)
    result = {"_": [], "Diffuse": [], "Mixed": [], "Dense": []}
    for index in range(len(answer['labels'])):
        label_id = answer['labels'][index]
        labels = list(result.keys())
        label_boxes = result.get(labels[label_id])
        label_boxes.append(answer['boxes'][index])
    image_with_boxes = utils.ShowImageWithBoxes(Img.permute(1, 2, 0).numpy(), answer, CLASSES)
    return image_with_boxes, result


def split_cups(image_bytes):
    return utils.split_cups(np.fromstring(image_bytes, np.uint8))

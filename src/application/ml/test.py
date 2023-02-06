import torch
from application.ml import utils
# import utils
# import application.ml.model as model
# import visualize
# import torchvision
from torchvision.io import decode_image
import numpy as np

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

# def apply_nms(orig_prediction, iou_thresh):
#     # torchvision returns the indices of the bboxes to keep
#     keep = torchvision.ops.nms(orig_prediction['boxes'], orig_prediction['scores'], iou_thresh)

#     final_prediction = orig_prediction
#     final_prediction['boxes'] = final_prediction['boxes'][keep]
#     final_prediction['scores'] = final_prediction['scores'][keep]
#     final_prediction['labels'] = final_prediction['labels'][keep]

#     return final_prediction



# def Predict(img_path, model):
#     Img = read_image(img_path)
#     answer = model([Img.float()])
#     # nms_prediction = apply_nms(answer, iou_thresh=0.7)
#     # print(nms_prediction)
#     return Img, answer

def loadImage(image_bytes):
    np_array = np.frombuffer(image_bytes, np.uint8)
    return torch.tensor(np_array)


def Predict(image_bytes, model):
    Img = decode_image(loadImage(image_bytes))
    answer = model([Img.float()])
    # nms_prediction = apply_nms(answer, iou_thresh=0.7)
    # print(nms_prediction)
    result = {"_": [], "Diffuse": [], "Mixed": [], "Dense": []}
    for index in range(len(answer[0]['labels'])):
        label_id = answer[0]['labels'][index]
        labels = list(result.keys())
        label_boxes = result.get(labels[label_id])
        label_boxes.append(answer[0]['boxes'][index])
    return result


# if __name__ == '__main__':

#     #############################################
#     # Load Model
#     #############################################
#     # ModelFit = utils.LoadModel(modelname=MODEL_NAME)

#     #############################################
#     # Predict data
#     #############################################
#     # ModelFit.eval()
#     file = open('imagee.png', "rb")
#     img, result = Predict(file.read(), ModelFit)
#     print(img)
#     print(result)
#     # visualize.ShowImageWithBoxes(img, boxes, CLASSES)

import os
import torch
import os
import cv2
import numpy as np

#############################################
# Dataset Parameters
#############################################
BATCH_SIZE = 1
NUM_WORKERS = 8
SHUFFLE = False
PATH_TO_MODEL = "application/ml"


def LoadModel(path: str = PATH_TO_MODEL, modelname: str = "skin.pth"):
    Model = torch.load(os.path.join(path, modelname))
    return Model.eval()


def SaveModel(model, path: str = PATH_TO_MODEL, modelname: str = "skin.pth"):
    save_dir = os.path.join(path, modelname)
    torch.save(model, save_dir)
    print(f"File was successful saved in: {save_dir}")

def ShowImageWithBoxes(img, target, classes):
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    for index in range(len(target['labels'])):
        box = target['boxes'][index]
        label = target['labels'][index]

        x1 = int(box[0].detach().numpy())
        y1 = int(box[1].detach().numpy())
        x2 = int(box[2].detach().numpy())
        y2 = int(box[3].detach().numpy())
        print(label)
        print(x1, y1, x2, y2)
        cv2.rectangle(
            img, (x1, y1), (x2, y2), (0, 0, 255), 5)
        cv2.putText(img, classes[label.detach()], (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    imS = cv2.resize(img, (960, 960))
    return img


def split_cups(image_array):
    img_original = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    if img_original.shape[0] > 4000:
        img = cv2.resize(img_original, (0, 0), fx=0.1, fy=0.1)
        coef = 10
    else:
        img = cv2.resize(img_original, (0, 0), fx=0.5, fy=0.5)
        coef = 5

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray_blurred = cv2.blur(gray, (1, 1))

    detected_circles = cv2.HoughCircles(gray_blurred,
                                        cv2.HOUGH_GRADIENT, 1, 1, param1=30,
                                        param2=15, minRadius=50, maxRadius=400)
    if detected_circles is not None:

        detected_circles = np.uint16(np.around(detected_circles))
        detected_circles = detected_circles[0][:10]
        detected_circles = sorted(detected_circles, key=lambda x: x[1])
        detected_circles = [detected_circles[0], detected_circles[-1]]
        last_h = 0
        first = True
        imgs = []
        for pt in detected_circles:
            img_copy = img_original.copy()
            a, b, r = pt[0] * coef, pt[1] * coef, pt[2] * coef
            if first:
                crop = img_original[0:b + r, 0:img_original.shape[1]]
                imS = cv2.resize(crop, (540, 960))
            else:
                crop = img_original[b - r:b + r, 0:img_original.shape[1]]
                imS = cv2.resize(crop, (540, 960))
            imgs.append(crop)
            first = False
        return imgs


def ReshapeLabels(labels: list, classes: list):
    labels_probability = torch.zeros(len(labels), classes)
    for i in range(len(labels)):
        labels_probability[i][labels[i]] = 1
    return labels_probability.float()


def image_to_grayscale(image_array):
    copy_gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    copy_gray_blurred = cv2.blur(copy_gray, (1, 1))
    return copy_gray_blurred


def join_images(first_image, second_image):
    return np.concatenate((first_image, second_image), axis=0)

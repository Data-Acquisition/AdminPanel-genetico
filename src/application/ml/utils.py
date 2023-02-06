import os
import torch
# import application.ml.dataset as dataset
# import torchvision.transforms as transforms
# from torch.utils.data import DataLoader, random_split

#############################################
# Dataset Parameters
#############################################
BATCH_SIZE = 1
NUM_WORKERS = 8
SHUFFLE = False
# PATH_TO_DATASET = "C:\\Users\\lunag\\Desktop\\Genetico\\dataset"4
PATH_TO_MODEL = "application/ml"


def LoadModel(path: str = PATH_TO_MODEL, modelname: str = "skin.pth"):
    Model = torch.load(os.path.join(path, modelname))
    return Model.eval()


def SaveModel(model, path: str = PATH_TO_MODEL, modelname: str = "skin.pth"):
    save_dir = os.path.join(path, modelname)
    torch.save(model, save_dir)
    print(f"File was successful saved in: {save_dir}")


# def PrepareData(path: str = PATH_TO_DATASET, transform: transforms = None):
#     data = dataset.TrainData(path, transform=transform)
#     trainLoader = DataLoader(data, batch_size=BATCH_SIZE, shuffle=SHUFFLE, num_workers=NUM_WORKERS)
#     return trainLoader


def ReshapeLabels(labels: list, classes: list):
    labels_probability = torch.zeros(len(labels), classes)
    for i in range(len(labels)):
        labels_probability[i][labels[i]] = 1
    return labels_probability.float()









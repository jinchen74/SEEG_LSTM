# ---------------------
# 数据的预处理的一些方法
# ---------------------

import os
import random
import sys
import time

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset
from torch.utils.data.sampler import Sampler

sys.path.append('../')
from util.util_file import matrix_normalization
import json

config = json.load(open("../DataProcessing/config/fig.json", 'r'))  # 需要指定训练所使用的数据
patient_test = config['patient_test']
print("patient_test is {}".format(patient_test))


def mini_data_folders(model_name ='mixed_data'):
    '''

    :param model: 训练的模式选择， 0：mixed, 1: inter_person
    :return:
    '''

    train_folder = '../data/seeg/{}/{}/train'.format(model_name, patient_test)
    test_folder = '../data/seeg/{}/{}/val'.format(model_name, patient_test)

    metatrain_folders = [os.path.join(train_folder, label)
                         for label in os.listdir(train_folder)
                         if os.path.isdir(os.path.join(train_folder, label))]

    metatest_folders = [os.path.join(test_folder, label)
                        for label in os.listdir(test_folder)
                        if os.path.isdir(os.path.join(test_folder, label))]
    random.seed(1)  # 原始论文中存在的固定
    random.shuffle(metatrain_folders)
    random.shuffle(metatest_folders)

    return metatrain_folders, metatrain_folders


class MiniDataTask(object):
    def __init__(self, character_folders, num_class, train_num, test_num):
        self.character_folders = character_folders
        self.num_classes = num_class
        self.train_num = train_num
        self.test_num = test_num

        class_folders = random.sample(self.character_folders, self.num_classes)
        labels = np.array(range(len(class_folders)))
        labels = dict(zip(class_folders, labels))
        samples = dict()

        self.train_roots = []
        self.test_roots = []
        for c in class_folders:
            temp = [os.path.join(c, x) for x in os.listdir(c)]
            samples[c] = random.sample(temp, len(temp))
            random.shuffle(samples[c])

            self.train_roots += samples[c][:train_num]
            self.test_roots += samples[c][train_num:train_num + test_num]

        self.train_labels = [labels[self.get_class(x)] for x in self.train_roots]
        self.test_labels = [labels[self.get_class(x)] for x in self.test_roots]
        # t = time.time()
        # random.seed(t)
        # random.shuffle(self.train_labels)
        # random.seed(t)
        # random.shuffle(self.train_roots)
        t = time.time()
        random.seed(t)
        random.shuffle(self.test_labels)
        random.seed(t)
        random.shuffle(self.test_roots)

    def get_class(self, sample):
        return os.path.join(*sample.split('/')[:-1])


class FewShotDataset(Dataset):

    def __init__(self, task, split='train', transform=None, target_transform=None):
        self.transform = transform  # Torch operations on the input image
        self.target_transform = target_transform
        self.task = task
        self.split = split
        self.image_roots = self.task.train_roots if self.split == 'train' else self.task.test_roots
        self.labels = self.task.train_labels if self.split == 'train' else self.task.test_labels

    def __len__(self):
        return len(self.image_roots)

    def __getitem__(self, idx):
        raise NotImplementedError("This is an abstract class. Subclass this class for your particular dataset.")


class Seegnet(FewShotDataset):

    def __init__(self, *args, **kwargs):
        super(Seegnet, self).__init__(*args, **kwargs)

    def __getitem__(self, idx):
        image_root = self.image_roots[idx]
        image = np.load(image_root)
        result = matrix_normalization(image, (130, 200))  # 矩阵的归一化
        result = result.astype('float32')
        result = torch.from_numpy(result)
        result = result[np.newaxis, :]
        # image = image.convert('RGB')
        # if self.transform is not None:
        #     image = self.transform(image)
        label = self.labels[idx]
        # if self.target_transform is not None:
        #     label = self.target_transform(label)
        return result, label


class ClassBalancedSampler(Sampler):
    ''' Samples 'num_inst' heatmap each from 'num_cl' pools
        of heatmap of size 'num_per_class' '''

    def __init__(self, num_per_class, num_cl, num_inst, shuffle=True):
        self.num_per_class = num_per_class
        self.num_cl = num_cl
        self.num_inst = num_inst
        self.shuffle = shuffle

    def __iter__(self):
        # return a single list of indices, assuming that items will be grouped by class
        if self.shuffle:
            batch = [[i + j * self.num_inst for i in torch.randperm(self.num_inst)[:self.num_per_class]] for j in
                     range(self.num_cl)]
        else:
            batch = [[i + j * self.num_inst for i in range(self.num_inst)[:self.num_per_class]] for j in
                     range(self.num_cl)]
        batch = [item for sublist in batch for item in sublist]

        if self.shuffle:
            random.shuffle(batch)
        return iter(batch)

    def __len__(self):
        return 1


def get_mini_imagenet_data_loader(task, num_per_class=1, split='train', shuffle=False):
    # normalize = transforms.Normalize(mean=[0.92206], std=[0.08426])
    dataset = Seegnet(task, split=split)

    # dataset = Seegnet(task, split=split, transform=transforms.Compose([transforms.ToTensor(), normalize]))

    if split == 'train':
        sampler = ClassBalancedSampler(num_per_class, task.num_classes, task.train_num, shuffle=shuffle)
    else:
        sampler = ClassBalancedSampler(num_per_class, task.num_classes, task.test_num, shuffle=shuffle)

    loader = DataLoader(dataset, batch_size=num_per_class * task.num_classes, sampler=sampler)

    return loader

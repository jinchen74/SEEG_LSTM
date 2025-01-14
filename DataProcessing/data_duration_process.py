'''
数据预处理，主要是讲数据进行划分，训练集和测试集以及验证集，划分的数据集用于few-shot learning, cnn 的训练效果, 这个处理方法是根据持续时间来做出选择
'''

import random

from RelationNet import *
import argparse
import numpy as np
import os

parser = argparse.ArgumentParser(description="data split")
parser.add_argument('-r', '--ratio', type=float, default=0.6)  # 将数据集划分为测试集，以及验证集
parser.add_argument('-v', '--val', type=float, default=0.2)
args = parser.parse_args()

# Hyper Parameters

TRAIN_RATIO = args.ratio
VAL_RATIO = args.val


def data_process():
    train_folder = "./seeg/train"
    test_folder = "./seeg/test"
    val_folder = './seeg/val'

    if os.path.exists(train_folder) is not True:
        os.makedirs(train_folder)
    else:
        os.system("rm -r ./seeg/train/*")
    if os.path.exists(test_folder) is not True:
        os.makedirs(test_folder)
    else:
        os.system("rm -r ./seeg/test/*")
    if os.path.exists(val_folder) is not True:
        os.makedirs(val_folder)
    else:
        os.system("rm -r ./seeg/val/*")

    path_normal = "sleep_normal"
    path_pre_seizure = "pre_seizure_wwt"
    path_within_seizure = "pre_seizure_bwt"

    train_folder_dir_normal = os.path.join(train_folder, path_normal)
    train_folder_dir_bwt = os.path.join(train_folder, path_pre_seizure)
    train_folder_dir_wwt = os.path.join(train_folder, path_within_seizure)

    test_folder_dir_normal = os.path.join(test_folder, path_normal)
    test_folder_dir_bwt = os.path.join(test_folder, path_pre_seizure)
    test_folder_dir_wwt = os.path.join(test_folder, path_within_seizure)

    val_folder_dir_normal = os.path.join(val_folder, path_normal)
    val_folder_dir_bwt = os.path.join(val_folder, path_pre_seizure)
    val_folder_dir_wwt = os.path.join(val_folder, path_within_seizure)

    if os.path.exists(train_folder_dir_normal) is not True:
        os.makedirs(train_folder_dir_normal)
    if os.path.exists(train_folder_dir_wwt) is not True:
        os.makedirs(train_folder_dir_wwt)
    if os.path.exists(train_folder_dir_bwt) is not True:
        os.makedirs(train_folder_dir_bwt)

    if os.path.exists(test_folder_dir_normal) is not True:
        os.makedirs(test_folder_dir_normal)
    if os.path.exists(test_folder_dir_wwt) is not True:
        os.makedirs(test_folder_dir_wwt)
    if os.path.exists(test_folder_dir_bwt) is not True:
        os.makedirs(test_folder_dir_bwt)

    if os.path.exists(val_folder_dir_normal) is not True:
        os.makedirs(val_folder_dir_normal)
    if os.path.exists(val_folder_dir_wwt) is not True:
        os.makedirs(val_folder_dir_wwt)
    if os.path.exists(val_folder_dir_bwt) is not True:
        os.makedirs(val_folder_dir_bwt)

    seeg = seegdata()
    tmp_normal = seeg.get_all_path_by_keyword('sleep')
    sleep_label0 = tmp_normal['LK']  # 正常人的睡眠时间
    path_dir_seizure = "../data/data_slice/split/preseizure"
    seeg.set_path_dir(path_dir_seizure)
    sleep_bwt = seeg.get_all_path_by_keyword('before_warning_time')
    sleep_bwt_label1 = sleep_bwt['LK']  # 发病前的一段时间,警戒线之外
    sleep_wwt = seeg.get_all_path_by_keyword('within_warning_time')
    sleep_wwt_label2 = sleep_wwt['LK']  # 发病前的一段时间,警戒线之内

    # print("normal sleep:{} pre seizure:{} awake:{} ".format(len(sleep_label0), len(sleep_label1), len(awake_label2))) # 三分类
    print("normal sleep:{} pre seizure:{}".format(len(sleep_label0), len(sleep_bwt_label1), len(sleep_wwt_label2)))
    random.shuffle(sleep_label0)
    random.shuffle(sleep_bwt_label1)
    random.shuffle(sleep_wwt_label2)
    min_data = min(len(sleep_label0), len(sleep_bwt_label1), len(sleep_wwt_label2))  # 让两个数据集的个数相等
    print("min_data:{}".format(min_data))

    sleep_label2 = sleep_wwt_label2[:min_data]
    sleep_label1 = sleep_bwt_label1[:min_data]
    sleep_label0 = sleep_label0[:min_data]
    train_num = int(TRAIN_RATIO * len(sleep_label0))
    test_num = int(VAL_RATIO * len(sleep_label0))

    print("train number:{}, test number:{}, val number:{}".format(train_num, test_num,
                                                                  len(sleep_label0) - test_num - train_num))

    for (i, p) in enumerate(sleep_label0):
        name = p.split('/')[-1]
        d = np.load(p)
        if i <= int(train_num):
            save_path = os.path.join(train_folder_dir_normal, name)
        else:
            if i < (train_num + test_num):
                save_path = os.path.join(test_folder_dir_normal, name)
            else:
                save_path = os.path.join(val_folder_dir_normal, name)

        np.save(save_path, d)

    print("Successfully write for normal data!!!")
    for (i, p) in enumerate(sleep_label1):
        name = p.split('/')[-1]
        d = np.load(p)
        if i <= int(train_num):
            save_path = os.path.join(train_folder_dir_bwt, name)
        else:
            if i <= (train_num + test_num):
                save_path = os.path.join(test_folder_dir_bwt, name)
            else:
                save_path = os.path.join(val_folder_dir_bwt, name)

        np.save(save_path, d)
    print("Successfully write for pre sleep data!!!")

    for (i, p) in enumerate(sleep_label2):
        name = p.split('/')[-1]
        d = np.load(p)
        if i <= int(len(sleep_label2) * TRAIN_RATIO):
            save_path = os.path.join(train_folder_dir_wwt, name)
        else:
            if i <= int(len(sleep_label2) * (TRAIN_RATIO + TRAIN_RATIO)):
                save_path = os.path.join(test_folder_dir_wwt, name)
            else:
                save_path = os.path.join(val_folder_dir_wwt, name)

        np.save(save_path, d)
    print("Successfully write for awake data!!!")


if __name__ == '__main__':
    data_process()

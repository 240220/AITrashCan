import os
import shutil
import random

random.seed(0)


def split_data(file_path, xml_path, new_file_path, train_rate, val_rate, test_rate):
    # 计算文件有关的信息
    each_class_image = []
    each_class_label = []
    for image in os.listdir(file_path):
        each_class_image.append(image)
    for label in os.listdir(xml_path):
        each_class_label.append(label)
    data = list(zip(each_class_image, each_class_label))
    total = len(each_class_image)

    # 随机打乱数据
    random.shuffle(data)
    each_class_image, each_class_label = zip(*data)
    train_images = each_class_image[0:int(train_rate * total)]
    val_images = each_class_image[int(train_rate * total):int((train_rate + val_rate) * total)]
    test_images = each_class_image[int((train_rate + val_rate) * total):]
    train_labels = each_class_label[0:int(train_rate * total)]
    val_labels = each_class_label[int(train_rate * total):int((train_rate + val_rate) * total)]
    test_labels = each_class_label[int((train_rate + val_rate) * total):]

    #  分别存储在不同的文件夹下
    for image in train_images:
        print(image)
        old_path = file_path + '/' + image
        new_path1 = new_file_path + '/' + 'images/train'
        if not os.path.exists(new_path1):
            os.makedirs(new_path1)
        new_path = new_path1 + '/' + image
        shutil.copy(old_path, new_path)

    for label in train_labels:
        print(label)
        old_path = xml_path + '/' + label
        new_path1 = new_file_path + '/' + 'labels/train'
        if not os.path.exists(new_path1):
            os.makedirs(new_path1)
        new_path = new_path1 + '/' + label
        shutil.copy(old_path, new_path)

    for image in val_images:
        old_path = file_path + '/' + image
        new_path1 = new_file_path + '/' + 'images/val'
        if not os.path.exists(new_path1):
            os.makedirs(new_path1)
        new_path = new_path1 + '/' + image
        shutil.copy(old_path, new_path)

    for label in val_labels:
        old_path = xml_path + '/' + label
        new_path1 = new_file_path + '/' + 'labels/val'
        if not os.path.exists(new_path1):
            os.makedirs(new_path1)
        new_path = new_path1 + '/' + label
        shutil.copy(old_path, new_path)

    for image in test_images:
        old_path = file_path + '/' + image
        new_path1 = new_file_path + '/' + 'images/test'
        if not os.path.exists(new_path1):
            os.makedirs(new_path1)
        new_path = new_path1 + '/' + image
        shutil.copy(old_path, new_path)

    for label in test_labels:
        old_path = xml_path + '/' + label
        new_path1 = new_file_path + '/' + 'labels/test'
        if not os.path.exists(new_path1):
            os.makedirs(new_path1)
        new_path = new_path1 + '/' + label
        shutil.copy(old_path, new_path)


if __name__ == '__main__':
    # 定义数据文件
    file_path = "E:/gongchuang/mydata/images"
    xml_path = "E:/gongchuang/mydata/labels"
    new_file_path = "./data/data07_split"
    split_data(file_path, xml_path, new_file_path, train_rate=0.7, val_rate=0.3, test_rate=0)
    # 分离训练集和测验集

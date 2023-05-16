import os


def mkdir(path):
    """
    创建文件夹的函数
    :param path: 文件夹路径
    :return: none
    """
    folder = os.path.exists(path)
    if not folder:  # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)  # makedirs 创建文件时如果路径不存在会创建这个路径


def mkcsv(path):
    """
    创建csv文件的函数
    :param path: csv文件路径
    :return: none
    """
    if os.path.exists(path):
        return
    with open(path, mode='w', encoding='utf-8') as ff:
        ff.close()

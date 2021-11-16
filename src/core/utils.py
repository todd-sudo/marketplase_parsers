import os


def check_folders(path: str):
    if not os.path.exists(path):
        os.makedirs(path)

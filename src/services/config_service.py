import os

class Config:
    cwd = os.path.realpath(__file__).split('\src')[0].replace('\\', '/')
    kaggleAuth = True
config = Config()
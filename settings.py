import os

GAME_NAME = "MongoMud"
LISTEN_PORTS = [4000]

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_PATH, 'src')
LOG_DIR = os.path.join(BASE_PATH, 'log')

IDLE_TIMEOUT = 3600

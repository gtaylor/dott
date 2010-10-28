import os

GAME_NAME = "Evennia"
LISTEN_PORTS = [4000]
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_PATH, 'src')

IDLE_TIMEOUT = 3600
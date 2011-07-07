import os

GAME_NAME = "Dawn of the Titans"
LISTEN_PORTS = [4000]

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_PATH, 'src')
LOG_DIR = os.path.join(BASE_PATH, 'log')

DATABASES = {
    'objects': {
        'NAME': 'dott_objects',
    },
    'config': {
        'NAME': 'dott_config',
    }
}

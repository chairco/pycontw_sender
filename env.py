import os
import pathlib
import logging

import dotenv

logger = logging.getLogger(__name__)

__all__ = ['ACCOUNT', 'PASSWORD', 'CC_MAIL']

ROOT_DIR_PATH = pathlib.Path(__file__).resolve().parent

dotenv_path = ROOT_DIR_PATH.joinpath('.env')
if dotenv_path.exists():
    dotenv.load_dotenv(str(dotenv_path))


ACCOUNT = os.getenv('ACCOUNT')

PASSWORD = os.getenv('PASSWORD')

CC_MAIL = os.getenv('CC_MAIL')


# This logs everything to stderr.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {    # Match access log style.
            'format': '[%(asctime)s] "%(levelname)s %(name)s" %(message)s',
            'datefmt': r'%d/%b/%Y %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 0,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'root': {
        'level': 0,
        'handlers': ['console'],
    }
}
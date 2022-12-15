import logging
import sys

logout = logging.getLogger()
stdout_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(levelname)s: %(message)s')
stdout_handler.setFormatter(formatter)
logout.addHandler(stdout_handler)
"""_levelToName = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
}"""
logout.setLevel(logging.WARNING)

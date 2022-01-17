"""Настроенный логер для использования экземпляра в проекте"""

import logging


def logger(module_name: str):
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s][%(asctime)s] %(name)s: %(message)s')
    return logging.getLogger(module_name)
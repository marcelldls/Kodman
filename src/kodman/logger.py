import logging


def init_logger(log):
    formatter = logging.Formatter("%(levelname)s:\t%(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    log.addHandler(handler)

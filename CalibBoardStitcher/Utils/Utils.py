import logging

def logging_config():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(filename)s.%(lineno)d: %(message)s'
    )

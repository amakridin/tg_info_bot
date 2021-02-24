import logging

logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("api.log")
fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'))
logger.addHandler(fh)
def info(msg):
    logger.info(msg)
def critical(msg):
    logger.critical(msg)
def fatal(msg):
    logger.fatal(msg)
def error(msg):
    logger.error(msg)

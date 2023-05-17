import logging
from logging.handlers import RotatingFileHandler

log_path = '/var/log/scrape/scrape.log'
handler = RotatingFileHandler(
    log_path, maxBytes=100000, backupCount=5)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger = logging.getLogger('apscheduler')
logger.addHandler(handler)

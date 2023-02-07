import logging
import sys

formatter = logging.Formatter('[%(name)s:%(lineno)d %(levelname)s]: %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)  # or use logging.INFO
ch.setFormatter(formatter)

from logging import getLogger
from os import environ


logger = getLogger(__name__)


DEBUG=environ.get('DEBUG', False)


def debug(*args):
    if DEBUG:
        logger.warning(*args)

    else:
        logger.debug(*args)
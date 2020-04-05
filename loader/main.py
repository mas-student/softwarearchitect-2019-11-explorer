from logging import getLogger, basicConfig

from loader.application import make_app
from loader.application import main


basicConfig()
logger = getLogger(__name__)


app = make_app()


if __name__ == '__main__':
    main(app)
from logging import getLogger, basicConfig

from backend.application import make_app, main


basicConfig()
logger = getLogger(__name__)


app = make_app()


if __name__ == '__main__':
    main()

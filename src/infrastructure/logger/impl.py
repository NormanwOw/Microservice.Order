import logging
from logging.handlers import RotatingFileHandler

from src.application.ports.logger import ILogger


class Logger(ILogger):
    def __init__(self) -> None:
        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.INFO)
        self.__uvicorn_logger = logging.getLogger('uvicorn')
        self.__uvicorn_logger.setLevel(logging.INFO)

        if not self.__logger.handlers:
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            file_handler = RotatingFileHandler(
                filename='logs/logs.log', mode='a', maxBytes=1_048_576, backupCount=3
            )
            file_handler.setFormatter(formatter)
            self.__logger.addHandler(file_handler)
            self.__uvicorn_logger.addHandler(file_handler)
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.__logger.addHandler(console_handler)

    def info(self, message: str) -> None:
        self.__logger.info(message)

    def error(self, message: str, exc_info: bool = True) -> None:
        self.__logger.error(message, exc_info=exc_info)

    def warning(self, message: str) -> None:
        self.__logger.warning(message)

    def debug(self, message: str) -> None:
        self.__logger.debug(message)


logger = Logger()

import logging
import time


class DwellistLogger:
    _logger = None  # Class-level logger instance

    @staticmethod
    def get_logger():
        if DwellistLogger._logger is None:
            DwellistLogger._logger = DwellistLogger.setup_logger()
        return DwellistLogger._logger

    @staticmethod
    def setup_logger():
        """Set up a logger"""
        # Create a logger
        logger = logging.getLogger("my_logger")
        logger.setLevel(logging.DEBUG)

        # Create a handler for writing to a file
        log_filename = f'my_log_{time.strftime("%Y_%m_%d")}.log'
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "[%(asctime)s %(levelname)s]\t%(message)s", datefmt="%H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Create a handler for printing to the console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(
            logging.INFO
        )  # You can set the desired logging level here
        console_formatter = logging.Formatter(
            "[%(asctime)s %(levelname)s]\t%(message)s", datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        return logger


def print_title():
    """Print the title from title.txt"""
    with open("misc/title.txt", "r", encoding="utf-8") as title_file:
        title = title_file.read()
    print(title)

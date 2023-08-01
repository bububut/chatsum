import os
import asyncio
import logging
from config import load_config
from wechaty_bot import main

def setup_logging():
    logging.getLogger().setLevel(logging.INFO)

    fmtstr = '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
    logformat = logging.Formatter(fmtstr)

    # Set up the file handler to log debug messages
    file_handler = logging.FileHandler('log/chatsum.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logformat)

    # Set up the console handler to log messages with level INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logformat)

    # Create the logger and add the handlers
    logger = logging.getLogger('chatsum')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


if __name__ == '__main__':
    setup_logging()
    load_config()
    asyncio.run(main())


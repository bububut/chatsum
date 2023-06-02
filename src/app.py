import os
import asyncio
import logging
from config import load_config
from wechaty_bot import main


if __name__ == '__main__':
    logformat = '%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | %(message)s'
    logging.basicConfig(level=logging.DEBUG, format=logformat)
    logger = logging.getLogger('chatsum')
    load_config()
    asyncio.run(main())


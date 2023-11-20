from stimulant_noise.stimulant_noise import run
import os

import logging

if __name__ == "__main__":
    loggin_file = "stimulant_noise.log"
    logging.basicConfig(filename=loggin_file, level=logging.DEBUG)
    logging.info("Starting noise generator")
    os.environ["PYTHONUNBUFFERED"] = "1"
    os.environ["GIN_MODE"] = "release"
    try:
        run()
    except Exception as e:
        logging.exception(e)
        raise e

from stimulant_noise.stimulant_noise import run

import logging

if __name__ == "__main__":
    loggin_file = "noise_generator.log"
    logging.basicConfig(filename=loggin_file, level=logging.DEBUG)
    logging.info("Starting noise generator")
    try:
        run()
    except Exception as e:
        logging.exception(e)
        raise e

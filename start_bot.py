from core.settings_bot import config
from core.main import client
import datetime as dt
import logging
import os

if __name__ == "__main__":
    log_level = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO
    }

    settings = config()
    log = logging.getLogger("LunaBOT")
    log.setLevel(log_level.get(settings['Logging']))
    utc = dt.datetime.utcnow()
    format_date = utc.strftime("%d-%m-%Y")
    try:
        f_handler = logging.FileHandler(f"./logs/LunaBOT-{format_date}.log")
    except FileNotFoundError:
        os.mkdir("./logs")
        f_handler = logging.FileHandler(f"./logs/LunaBOT{format_date}.log")

    c_handler = logging.StreamHandler()
    formatter1 = logging.Formatter(
        "\033[01;38;05;15m%(asctime)s \033[01;38;05;135m[%(levelname)s]\033[01;38;05;15m[%(name)s] - %(message)s",
        datefmt='%d-%b-%y %H:%M:%S')
    formatter2 = logging.Formatter("%(asctime)s [%(levelname)s][%(name)s] - %(message)s", datefmt='%d-%b-%y %H:%M:%S')

    f_handler.setFormatter(formatter2)
    c_handler.setFormatter(formatter1)
    log.addHandler(f_handler)
    log.addHandler(c_handler)

    log.debug("Hello world")

    client.run(settings["token_bot"])

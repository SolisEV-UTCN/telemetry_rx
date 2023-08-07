from pathlib import Path

import logging
import shutil
from typing import List


def create_config_file() -> None:
    """If no config.ini file exists, then creates it from the template"""
    config = Path("config", "config.ini")
    template = Path("config", "config_template.ini")
    if not config.exists():
        logging.warn("No configuration file. Creating fresh copy, consider checking src/config/config.ini.")
        shutil.copyfile(template, config, False)

if __name__ == "__main__":
    create_config_file()
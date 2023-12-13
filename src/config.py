from debugger import *
from pathlib import Path

import configparser


config = configparser.ConfigParser()
res = config.read(Path(__file__).parent.parent / "data" / "config.cfg")

STEAMPATH: str = config.get("Paths", "STEAMPATH")
MAFILESPATH: str = config.get("Paths", "MAFILESPATH")
WIDTH: int = config.getint("Dimensions", "WIDTH")
HEIGHT: int = config.getint("Dimensions", "HEIGHT")
OWNERID: str = config.get("Other", "OWNERID")

debug("CONFIG WAS IMPORTED")

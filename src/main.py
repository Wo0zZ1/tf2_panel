import json
import gui
import asyncio
import pyautogui
import keyboard
import steam.guard

from pathlib import Path
from tradeHandler import TradeHandler
from position import Position
from debugger import *

import config as cfg


def readAccountsFile(filePath: str):
    with open(filePath, "r") as f:
        lines = f.readlines()
    accounts = {}
    for line in lines:
        parts = line.strip().split(":")
        if len(parts) == 2:
            login, password = parts
            accounts[login] = password
    if len(accounts) == 0:
        raise Exception("Accounts file is bad")
    return accounts


def readAPIsFile(filePath: str) -> str:
    with open(filePath, "r") as f:
        lines = f.readlines()
    accounts = {}
    for line in lines:
        parts = line.strip().split(":")
        if len(parts) == 2:
            login, api = parts
            accounts[login] = api
    return accounts


def readMafilesFolder(folderPath: str):
    mafiles = {}
    for filename in Path(folderPath).glob("*.maFile"):
        with open(filename, "r") as f:
            content = f.read().strip()
        mafiles[filename.stem] = json.loads(content)
    if len(mafiles) == 0:
        raise Exception("Folder does't contain maFile's")
    return mafiles


def getMafileByName(mafiles: dict, name: str) -> dict:
    for id, mafile in mafiles.items():
        if "account_name" in mafile and mafile["account_name"] == name:
            return mafile
    raise Exception("ERROR: can't get myFile by name")


def getAPI(APIs: dict, name: str) -> str | None:
    return APIs[name] if name in APIs else None


def getSecret(mafile: dict) -> dict:
    secret = {}
    elements = [
        "account_name",
        "shared_secret",
        "serial_number",
        "revocation_code",
        "uri",
        "server_time",
        "token_gid",
        "identity_secret",
        "secret_1",
        "status",
    ]
    for type in elements:
        try:
            secret[type] = mafile[type]
        except Exception:
            raise Exception("ERROR: bad parsing maFile")
    return secret


def getGuard(maFile: dict):
    guard = {}
    guardContent = ["secret_1", "shared_secret", "identity_secret"]
    guardContent_session = [
        ("SteamID", "steamid"),
        ("AccessToken", "access_token"),
        ("RefreshToken", "refresh_token"),
    ]
    for type in guardContent:
        try:
            guard[type] = maFile[type]
        except Exception as error:
            raise Exception(error)
    for typeFile, typeGuard in guardContent_session:
        try:
            guard[typeGuard] = maFile["Session"][typeFile]
        except Exception as error:
            raise Exception(error)
    return guard


def writeGuardFile(maFile: dict, name: str):
    guard = getGuard(maFile)
    with open(Path(__file__).parent.parent / "guards" / f"{name}.json", "w") as f:
        f.write(json.dumps(guard))


def enterTFA(sa: steam.guard.SteamAuthenticator):
    x, y = 840, 480
    pyautogui.moveTo(x, y)
    pyautogui.click()
    for char in sa.get_code():
        pyautogui.press(char)


def endTask(hotKey: str, process=None, trader: TradeHandler = None):
    debug(f"EndTask for '{hotKey}'")

    if trader is not None:
        try:
            debug("Trying to send offer")
            result = trader.createOffer()
        except Exception as error:
            debug(f"Error sending trade offer: '{error}'")
        else:
            debug(f"Trade was created success with result: '{result}'")
    if process is not None:
        try:
            debug("Trying to kill process")
            process.kill()
        except Exception as error:
            debug(f"Error process killing: '{error}'")
        else:
            debug(f"Process was killed success")
    keyboard.remove_hotkey(hotKey)
    debug(f"Hotkey '{hotKey}' was removed success")


async def runAccount(
    position: Position,
    login: str,
    password: str,
    secret: dict,
    API: str | None,
):
    debug(f"Account ${login} has been started")
    trader: TradeHandler | None = None
    if API is not None:
        trader = TradeHandler(
            Path(__file__).parent.parent / "guards" / f"{login}.json",
            login,
            password,
            API,
        )
        trader.login()

    process = await asyncio.create_subprocess_exec(
        Path(cfg.STEAMPATH),
        "-noverifyfiles",
        "-login",
        login,
        password,
        "-language",
        "russian",
        "-noreactlogin",
        "-silent",
        "-no-browser",
        "-offline",
        "-nosteamcontroller",
        "-applaunch",
        "440",
        "-novid",
        "-window",
        "-w",
        str(cfg.WIDTH),
        "-h",
        str(cfg.HEIGHT),
        "-nosrgb",
        "-nosound",
        "-nodcaudio",
        "-nofbo",
        "-nomsaa",
        "-low",
        "-noaafonts",
        "-nojoy",
        "-invisible",
        "-console",
        "+fps_max 30",
        "-x",
        str(position.x),
        "-y",
        str(position.y),
    )

    debug('Wait "Ctrl + Shift + P" for entering SA')
    keyboard.wait("Ctrl + Shift + P")

    enterTFA(steam.guard.SteamAuthenticator(secret))

    hotKey = f"Ctrl + Shift + {str(position.index)}"
    keyboard.add_hotkey(
        hotKey,
        endTask,
        args=[hotKey, process, trader],
    )
    position.next()
    debug('Wait "Ctrl + Shift + P" to finish')
    keyboard.wait("Ctrl + Shift + P")


def startAccounts(accounts: dict[str, str], APIs: dict, maFiles: dict):
    position: Position = Position(0, 0)
    for login, password in accounts.items():
        try:
            mafile = getMafileByName(maFiles, login)
            secret = getSecret(mafile)
            API = getAPI(APIs, login)
            writeGuardFile(mafile, login)
        except Exception as error:
            debug(error)
            continue
        try:
            asyncio.run(runAccount(position, login, password, secret, API))
        except Exception as error:
            debug(f"ERROR IN runAccount() | {error}")


def start():
    accounts = readAccountsFile(Path(__file__).parent.parent / "data" / "logpass.txt")
    APIs = readAPIsFile(Path(__file__).parent.parent / "data" / "api.txt")
    mafiles = readMafilesFolder(Path(cfg.MAFILESPATH))
    selected = gui.show_modal_window(accounts.keys())
    selectedAccounts = {}
    for account in selected:
        selectedAccounts[account] = accounts[account]
    if len(selectedAccounts) == 0:
        raise Exception("Bad selecting accounts")
    startAccounts(selectedAccounts, APIs, mafiles)


if __name__ == "__main__":
    try:
        start()
    except Exception as error:
        debug(f"The program was terminated with an error: '{error}'")
    else:
        print("wait")
        keyboard.wait()

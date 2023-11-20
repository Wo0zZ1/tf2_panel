import os
import time
import json
import steam.guard
import gui
import asyncio
import pyautogui

STEAMPATH: str = ""  # write path steam.exe
MAFILESPATH: str = ""  # write path sda/mafiles folder
WIDTH: int = 400  # set the window width
HEIGHT: int = 300  # set the window height


class Pos:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def next(self):
        if self.x + WIDTH <= 1920 - WIDTH:
            self.x += WIDTH
        elif self.y + HEIGHT <= 1080 - HEIGHT:
            self.x = 0
            self.y += HEIGHT

    x: int = 0
    y: int = 0


def readAccountsFile(filename):
    with open(filename, "r") as f:
        lines = f.readlines()
    accounts = {}
    for line in lines:
        parts = line.strip().split(":")
        if len(parts) == 2:
            login, password = parts
            accounts[login] = password
    return accounts


def readMafilesFolder(folder):
    mafiles = {}
    for filename in os.listdir(folder):
        if filename.endswith(".maFile"):
            name = os.path.splitext(filename)[0]
            path = os.path.join(folder, filename)
            with open(path, "r") as f:
                content = f.read().strip()
            mafiles[name] = json.loads(content)
    return mafiles


def getMafileByName(mafiles: dict, name: str) -> dict:
    for id, mafile in mafiles.items():
        if mafile["account_name"] == name:
            return mafile
    return None


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
        secret[type] = mafile[type]
    return secret


def tfa(sa: steam.guard.SteamAuthenticator):
    x, y = 840, 480
    pyautogui.moveTo(x, y)
    pyautogui.click()
    for char in sa.get_code():
        pyautogui.press(char)


async def runAccount(
    position: Pos, login: str, password: str, sa: steam.guard.SteamAuthenticator
):
    print(f"Account ${login} has been started")

    process = await asyncio.create_subprocess_exec(
        STEAMPATH,
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
        str(WIDTH),
        "-h",
        str(HEIGHT),
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

    # print("sleep 30") #
    time.sleep(30)
    tfa(sa)
    # print("sleep 60") #
    time.sleep(60)


def startAccounts(accounts: dict, mafiles: dict):
    position: Pos = Pos(0, 0)
    for login, password in accounts.items():
        mafile = getMafileByName(mafiles, login)
        secret = getSecret(mafile)
        if secret == None:  # bad secret
            print("ERROR: parsing secret", mafile)
            return
        sa = steam.guard.SteamAuthenticator(secret)
        asyncio.run(runAccount(position, login, password, sa))
        position.next()


def start():
    accounts = readAccountsFile("./logpass.txt")
    mafiles = readMafilesFolder(MAFILESPATH)
    selected = gui.show_modal_window(accounts.keys())
    selectedAccounts = {}
    for i in accounts:
        if i in selected:
            selectedAccounts[i] = accounts[i]
    if len(selectedAccounts) == 0:  # bad select
        print("ERROR: account selecting")
        return
    startAccounts(selectedAccounts, mafiles)


if __name__ == "__main__":
    start()
    time.sleep(600)

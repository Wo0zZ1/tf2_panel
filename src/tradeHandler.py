from steampy.client import SteamClient, Asset
from steampy.models import GameOptions
import config as cfg


class TradeHandler:
    def __init__(
        self,
        maFilePath: str = None,
        login: str = None,
        password: str = None,
        API: str = None,
    ) -> None:
        self.maFilePath = maFilePath
        self.username = login
        self.password = password
        self.steamKey = API
        self.steamClient: None | SteamClient = None

    def login(self) -> None:
        self.steamClient = SteamClient(self.steamKey)
        self.steamClient._session.cookies.set("steamRememberLogin", "true")
        self.steamClient.login(self.username, self.password, self.maFilePath)

    def getInventory(self) -> dict:
        return self.steamClient.get_my_inventory(GameOptions.TF2)

    def _getTradeableItems(self) -> list:
        tradeItems = []
        for item in self.getInventory().values():
            if item["tradable"]:
                tradeItems.append(item["id"])
        return tradeItems

    def _createAssets(self) -> list[Asset]:
        assets: list[Asset] = []
        for item in self._getTradeableItems():
            assets.append(Asset(item, GameOptions.TF2))
        return assets

    def createOffer(self) -> dict:
        result = self.steamClient.make_offer(
            self._createAssets(), [], cfg.OWNERID, f"Drop from {self.username}"
        )
        return result

from abc import ABC, abstractmethod

class BrokerProvider(ABC):
    @abstractmethod
    def get_connection_status(self) -> dict:
        pass

    @abstractmethod
    def get_margins(self) -> dict:
        pass

    @abstractmethod
    def get_positions(self) -> dict:
        pass

    @abstractmethod
    def get_orders(self) -> dict:
        pass

    @abstractmethod
    def place_order(self, tradingsymbol: str, transaction_type: str, quantity: int, product: str, order_type: str, price: float = 0.0) -> dict:
        pass


class DataProvider(ABC):
    @abstractmethod
    def get_historical_candles(self, symbol: str, interval: str, period: str) -> object:
        pass

    @abstractmethod
    def get_realtime_candles(self, symbol: str, interval: str, period: str) -> object:
        pass

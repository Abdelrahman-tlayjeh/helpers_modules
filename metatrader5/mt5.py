import MetaTrader5 as mt
from datetime import datetime
import pandas as pd


class Mt5:
    # trades types (actions)
    _TRADES_TYPES = {"BUY": mt.ORDER_TYPE_BUY, "SELL": mt.ORDER_TYPE_SELL}
    # filling types
    _TRADES_FILLING_TYPES = {
        "IOC": mt.ORDER_FILLING_IOC,
        "FOK": mt.ORDER_FILLING_FOK,
        "RETURN": mt.ORDER_FILLING_RETURN,
    }

    def __init__(
        self,
        server: str,
        login: int,
        password: str,
        pair_extension: str = "",
        filling_type: str = "IOC",
    ) -> None:
        """
        Args:
            server : broker server
            login : MetaTrader5 login id
            password : MetaTrader5 login password
            pair_extension (optional) : in case that pairs are not the default (e.g: "EURUSDm#" for micro accounts, the extension is "m#"). default is empty string
            filling_type (optional) : the filling type, can be "IOC", "FOK", or "RETURN", depending on used broker, default is "IOC"
            acceptable_change_in_price (optional) : the acceptable change in entry price at the moment of executing the trade (in pip), default is 10
        """
        # connections config
        self._SERVER = server
        self._LOGIN_ID = login
        self._PASSWORD = password
        # other config
        self._PAIR_EXTENSION = pair_extension
        self._filling_type = filling_type

    def __repr__(self) -> str:
        return f"Mt5('{self._SERVER}', {self._LOGIN_ID}, '{self._PASSWORD}', '{self._PAIR_EXTENSION}', '{self._filling_type}')"

    def __str__(self) -> str:
        return f"Mt5(login: '{self._LOGIN_ID}', server: '{self._SERVER}')"

    # ========== connect/disconnect ==========#
    def connect(self) -> None:
        """
        start a connection with MT5 terminal, will raise an Exception in case of any error
        """
        mt.initialize()
        if not mt.login(
            login=self._LOGIN_ID,
            server=self._SERVER,
            password=self._PASSWORD,
            timeout=60_000,
        ):
            raise Exception(f"Failed to connect with MT5 terminal: {self.last_error}")

    def disconnect(self) -> None:
        """perform MetaTrader5.shutdown()"""
        mt.shutdown()

    # ========== account info properties ==========#
    def _get_info(self):
        """return MetaTrader5.account_info()"""
        return mt.account_info()

    @property
    def account_info(self) -> dict:
        """all account information"""
        return mt.account_info()._asdict()

    @property
    def account_leverage(self) -> int:
        """used leverage"""
        return self._get_info().leverage

    @property
    def account_balance(self) -> float:
        """current account balance"""
        return self._get_info().balance

    @property
    def account_equity(self) -> float:
        """current account equity"""
        return self._get_info().equity

    @property
    def account_profit(self) -> float:
        """current account profit"""
        return self._get_info().profit

    @property
    def account_margins(self) -> dict:
        """account margin levels
        returns:
             dict like -> {
                "used": float
                "free": float
                "level": float
            }
        """
        info = self._get_info()
        return {
            "used": info.margin,
            "free": info.margin_free,
            "level": info.margin_level,
        }

    # ========== MT vars/constants ==========#
    @property
    def SUCCESSFULLY_OPEN(self) -> int:
        """the constant of a succeed open trade"""
        return mt.TRADE_RETCODE_DONE

    @property
    def last_error(self) -> tuple:
        """last MetaTrader5 error"""
        return mt.last_error()

    # ========== pairs info ==========#
    def _get_pair_info(self, pair: str) -> dict:
        """
        return all pair info,
        it will raise an Exception if the pair is invalid or any unexpected error occur
        """
        if info := mt.symbol_info(pair):
            return info._asdict()
        # failed
        raise Exception(f"failed to find '{pair}': {self.last_error}")

    def get_current_pair_price(self, pair: str) -> dict:
        """
        return current [buy] and [sell] prices of pair,
        it will raise an Exception if the pair is invalid or any unexpected error occur
        returns:
        dict like -> {
            "sell": float
            "buy": float
        }
        """
        if info := self._get_pair_info(pair):
            return {"sell": info["bid"], "buy": info["ask"]}

    # ========== helpers ==========#
    def _calc_pips(self, price1: float, price2: float) -> int:
        """calculate the difference between two prices in pips"""
        # JPY pairs
        if str(price1).index(".") >= 2:
            vp = 0.01
        # all other forex pairs
        else:
            vp = 0.0001

        return int(round(abs(price1 - price2) / vp))

    def _is_entry_price_valid(
        self,
        pair: str,
        entry_price: float,
        action: str,
        acceptable_change_in_price: int,
    ) -> bool:
        """
        check if entry_price is valid (the difference between entry_price and the current price is less than or equal acceptable_change_in_price)
        """
        return (
            self._calc_pips(
                entry_price,
                self.get_current_pair_price(pair)["buy" if action == "BUY" else "sell"],
            )
            <= acceptable_change_in_price
        )

    # ========== open/close trade ==========#
    def open_trade(
        self,
        pair: str,
        type: str,  # 'BUY'|'SELL'
        volume: float,
        entry: float,
        sl: float,
        tp: float,
        magic: int = 1000,
        note: str = "",
        acceptable_change_in_price: int = 10,
    ) -> mt.OrderSendResult:
        """
        execute the trade, it will return MetaTrader5.OrderSendResult object if trade is successfully opened,
        otherwise, it will raise an Exception
        Args:
            pair : e.g "EURUSD"
            type : "BUY" or "SELL"
            volume : the lot size
            entry : the entry price
            sl: the stop loss
            tp: the take profit
            magic (optional) : the magic number, default is 1000
            note (optional) : a note, default is empty string
            acceptable_change_in_price (optional) : the acceptable change in entry price at the moment of executing the trade (in pip), default is 10
        """

        # check if entry_price is valid
        if not self._is_entry_price_valid(
            pair, entry, type, acceptable_change_in_price
        ):
            raise Exception(
                f"Entry price is invalid: entry='{entry}'; current price = {self.get_current_pair_price(pair)}"
            )

        # send order request to terminal
        try:
            result = mt.order_send(
                {
                    "action": mt.TRADE_ACTION_DEAL,
                    "symbol": pair.upper() + self._PAIR_EXTENSION,
                    "volume": volume,
                    "type": self._TRADES_TYPES[type.upper()],
                    "price": entry,
                    "sl": sl,
                    "tp": tp,
                    "magic": magic,
                    "comment": note,
                    "type_time": mt.ORDER_TIME_GTC,
                    "type_filling": self._TRADES_FILLING_TYPES[self._filling_type],
                }
            )
        # --- Trade is not executed ---#
        except Exception as e:
            raise Exception(
                f"Unexpected error occur when trying to open the trade: {e}"
            )

        # --- Trade is executed without exception ---#
        # if the return is None
        if result is None:
            raise Exception(f"Failed to open Trade (returns None): {self.last_error}")

        # if succeed
        if result.retcode == self.SUCCESSFULLY_OPEN:
            return result

        # not succeed
        # if auto trading option is disabled
        if result.retcode == 10027:
            raise Exception(f"Failed to open trade because AutoTrading is disabled!")
        # invalid stops (TP|SL)
        if result.retcode == 10016:
            raise Exception(f"Failed to open trade due to invalid stops!")
        # other errors
        raise Exception(
            f"MT5 reject the trade: retcode={result.retcode} [{result.comment}]"
        )

    # ========== Get historical info ==========#
    def get_history(
        self, from_date: datetime, to_date: datetime = datetime.now(), group: str = "*"
    ) -> pd.DataFrame:
        """get history of all deals within the given period
        Args:
            from_date (datetime): the start date
            to_date (datetime, optional): the end date. Defaults to datetime.now().
            group (str, optional): the needed group e.g: "EURUSD". Defaults to "*" (all).
        Returns:
            pd.DataFrame: a dataframe contains all deals within the given period
        """
        history = mt.history_deals_get(from_date, to_date, group=group)
        return pd.DataFrame(list(history), columns=history[0]._asdict().keys())

    def get_deal(self, deal_ticket: int) -> "dict|None":
        """get deal info of the given ticket
        Args:
            deal_ticket (int): deal ticket
        Returns:
            dict|None: a dict contains the deal info, None if no deal found with the given ticket
        """
        deals = mt.history_deals_get(ticket=deal_ticket)
        return deals[0]._asdict() if deals else None

    def get_order(self, order_ticket: int) -> "dict|None":
        """get order info of the given ticket
        Args:
            order_ticket (int): order ticket
        Returns:
            dict|None: a dict contains the order info, None if no order found with the given ticket
        """
        orders = mt.history_orders_get(ticket=order_ticket)
        return orders[0]._asdict() if orders else None

    def get_order_deals(self, order_ticket: int) -> "tuple[dict]|None":
        """get all deals of the given order ticket
        Args:
            order_ticket (int): order/position ticket
        Returns:
            tuple|None: a tuple contains all deals of the given position ticket, None if no deals found
        """
        deals = mt.history_deals_get(position=order_ticket)
        return tuple(map(lambda d: d._asdict(), deals)) if deals else None

    def get_trade_result(self, order_ticket: int) -> "dict|None":
        """get trade result of the given order ticket
        Args:
            order_ticket (int): order/position ticket
        Returns:
            dict|None: a dict contains the trade(closing deal) result, None ticket is not found or the order is not closed yet
        """
        deals = self.get_order_deals(order_ticket)
        if deals is None or len(deals) < 2:
            return None
        return self.get_deal(deal_ticket=deals[-1]["ticket"])

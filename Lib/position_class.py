
class Position():
    """
    Position class that handles a trade position. Opens and closes
    positions and calculats the return

    Notes:
    - Currently assumes positions are fixed size of "one unit" so
    so returns are given in terms of percentage rather than absolute
    amount
    - Only handles one position at a time

    To Do:
    - Add a position ID system for trade history analysis
    - Add position sizings to give returns in absolute amounts
    """

    def __init__(self):
        self._pos = 0
        self._entryprice = 0
        self._exitprice = 0
        self._tradereturn = 0

    def setEntryPrice(self, price):
        """
        Sets entry price for a position
        """

        self._entryprice = price

    def setExitPrice(self, price):
        """
        Sets exit price for a position
        """

        self._exitprice = price

    def setTradeReturn(self):
        """
        Calculates the round trip trade return as a fraction.
        """

        Exit, Entry = self.getExitPrice(), self.getEntryPrice()
        self._tradereturn = self._pos*(Exit - Entry)/abs(Entry)

    def getEntryPrice(self):
        """
        Gets entry price of a position
        """

        return self._entryprice

    def getExitPrice(self):
        """
        Gets exit price for a position
        """

        return self._exitprice

    def getTradeReturn(self):
        """
        Gets trade returns
        """
        return self._tradereturn

    def open(self, price, pos_type, fee=0):
        """
        Opens a position.

        Inputs:
        - price:            (double) price to open a position
        - pos_type:         (str) 'L' or 'S' for long or short position
        - fee:              (double) fractional trading fee
        """

        if fee >= 1:
            raise ValueError("trading fee must be less than 1")
        if self._pos != 0:
            raise RuntimeError("Cannot open position."
                               + "A position is already open")

        self.setEntryPrice(price)
        if pos_type == 'L':
            self._pos = 1*(1-fee)
        if pos_type == 'S':
            self._pos = -1*(1-fee)

    def close(self, price, fee=0):
        """
        Closes a position.

        Inputs:
        - price:            (double) price at which to close a position
        - fee:              (double) fractional trading fee
        """

        if fee >= 1:
            raise ValueError("trading fee must be less than 1")
        if self._pos == 0:
            raise RuntimeError("No open position to close")

        self.setExitPrice(price)
        self._pos *= (1 - fee)
        self.setTradeReturn()
        self._pos = 0

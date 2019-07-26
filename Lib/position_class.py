
class Position():

    def __init__(self):
        self._pos = 0
        self._entryprice = 0
        self._exitprice = 0

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

    def openPostition(self, price, pos_type, fee=0):
        """
        Opens a position.

        Inputs:
        - price:            (double) price to open a position
        - pos_type:         (str) 'L' or 'S' for long or short position
        - fee:              (double) fractional trading fee
        """

        if fee >= 1:
            raise ValueError("trading fee must be less than 1")

        self.setEntryPrice(price)
        if pos_type == 'L':
            self._pos = 1*(1-fee)
        if pos_type == 'S':
            self._pos = -1*(1-fee)
    
    def closePosition(self, price):
        """
        Closes a position.

        Inputs:
        - price:            (double) price at which to close a position

        Outputs:
        - tradeReturn       (double) fractional return of the round trip
                            trade.
        """
        self.setExitPrice(price)
        Exit, Entry = self.getExitPrice(), self.setEntryPrice()
        tradeReturn = (Exit - Entry)/abs(Entry)
        self._pos = 0

        return tradeReturn



    


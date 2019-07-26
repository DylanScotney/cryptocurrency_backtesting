from pytest import raises, approx

from ..Lib.position_class import Position


def test_initialisation():
    """
    Tests correct initialisation
    """

    position = Position()
    assert(position.getPosition() == 0)
    assert(position.getEntryPrice() == 0)
    assert(position.getExitPrice() == 0)
    assert(position.getTradeReturn() == 0)

def test_setEntryPrice():
    """
    Tests entry price setter
    """

    position = Position()
    position.setEntryPrice(5)
    assert(position.getEntryPrice() == 5)    
    position.setEntryPrice(-5)
    assert(position.getEntryPrice() == -5)    
    position.setEntryPrice(0)
    assert(position.getEntryPrice() == 0)    
    position.setEntryPrice(5.2)
    assert(position.getEntryPrice() == approx(5.2))

def test_setExitPrice():
    """
    Tests exit price setter
    """

    position = Position()
    position.setExitPrice(5)
    assert(position.getExitPrice() == 5)
    position.setExitPrice(-5)
    assert(position.getExitPrice() == -5)    
    position.setExitPrice(0)
    assert(position.getExitPrice() == 0)    
    position.setExitPrice(5.2)
    assert(position.getExitPrice() == approx(5.2))

def test_calcTradeReturn_longs():
    """
    Tests calcTradeReturns for long positions
    """

    position = Position()
    position.setEntryPrice(5)
    position.setExitPrice(10)
    position._pos = 1
    position.calcTradeReturn()
    assert(position.getTradeReturn() == approx(1.0))

    position.setEntryPrice(5)
    position.setExitPrice(2.5)
    position._pos = 1
    position.calcTradeReturn()
    assert(position.getTradeReturn() == approx(-0.5))

    position.setEntryPrice(5)
    position.setExitPrice(5)
    position._pos = 1
    position.calcTradeReturn()
    assert(position.getTradeReturn() == approx(0))

def test_calcTradeReturn_shorts():
    """
    Tests calcTradeReturns for short positions
    """

    position = Position()
    position.setEntryPrice(5)
    position.setExitPrice(10)
    position._pos = -1
    position.calcTradeReturn()
    assert(position.getTradeReturn() == approx(-1.0))

    position.setEntryPrice(5)
    position.setExitPrice(2.5)
    position._pos = -1
    position.calcTradeReturn()
    assert(position.getTradeReturn() == approx(0.5))

    position.setEntryPrice(5)
    position.setExitPrice(5)
    position._pos = -1
    position.calcTradeReturn()
    assert(position.getTradeReturn() == approx(0))

def test_open_fee_failure():
    """
    Checks for exception if fee >= 1
    """

    position = Position()
    with raises(ValueError):
        position.open(5, 'L', fee=1)
    
    with raises(ValueError):
        position.open(5, 'L', fee=1.5)

def test_open_pos_failure():
    """
    Checks for exception if open position and self._pos != 0
    """
    
    position = Position()

    position._pos = 1
    with raises(RuntimeError):
        position.open(5, 'L')
    
    position._pos = -1
    with raises(RuntimeError):
        position.open(5, 'L')

def test_open_pos_type_failure():
    """
    Checks for exception if position type not recognised
    """

    position = Position()
    
    with raises(ValueError):
        position.open(5, 1)
    
    with raises(ValueError):
        position.open(5, 'noncompatible string')

def test_open_price_failure():
    """
    Checks exception is raised for incorrect price type
    """

    position = Position()
    with raises(ValueError):
        position.open('5', 'L')
    
def test_open():
    """
    Tests opening position
    """

    position = Position()
    position.open(5, 'L')
    assert(position.getEntryPrice() == 5)
    assert(position.getPosition() == 1)

    position._pos = 0
    position.open(5, 'S')
    assert(position.getEntryPrice() == 5)
    assert(position.getPosition() == -1)

def test_close_fee_failure():
    """
    Checks exception is raised for incorrect fee size
    """

    position = Position()
    position._pos = 1
    with raises(ValueError):
        position.close(5, fee=1)
    with raises(ValueError):
        position.close(5, fee=1.5)

def test_close_pos_failue():
    """
    Checks exception is raised if no position to close
    """

    position = Position()
    with raises(RuntimeError):
        position.close(5)

def test_close_longs():
    """
    Tests closing of longs
    """

    position = Position()

    position.open(5, 'L')
    position.close(10)
    assert(position.getPosition() == 0)
    assert(position.getTradeReturn() == approx(1.0))

    position.open(5, 'L')
    position.close(2.5)
    assert(position.getPosition() == 0)
    assert(position.getTradeReturn() == approx(-0.5))

    position.open(5, 'L')
    position.close(5)
    assert(position.getPosition() == 0)
    assert(position.getTradeReturn() == approx(0.0))

def test_close_shorts():
    """
    Tests closing of shorts
    """

    position = Position()

    position.open(5, 'S')
    position.close(10)
    assert(position.getPosition() == 0)
    assert(position.getTradeReturn() == approx(-1.0))

    position.open(5, 'S')
    position.close(2.5)
    assert(position.getPosition() == 0)
    assert(position.getTradeReturn() == approx(0.5))

    position.open(5, 'S')
    position.close(5)
    assert(position.getPosition() == 0)
    assert(position.getTradeReturn() == approx(0.0))

def test_trading_fees():
    """
    Tests trading fee logic
    """

    position = Position()

    position.open(5, 'L', fee=0.1)
    position.close(10, fee=0.1)
    assert(position.getTradeReturn() == approx(0.81))

    position.open(5, 'L', fee=0.1)
    position.close(5)
    assert(position.getTradeReturn() == approx(-0.1))

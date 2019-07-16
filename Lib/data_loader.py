
class dataLoader():
    """
    Context class for loading data.
    Has strategies derived from fileLoader, webLoader classes.
    See readme.md for more info.
    """

    def __init__(self, strategy):
        self._strategy = strategy

    def get_data(self):
        return self._strategy.get_data()

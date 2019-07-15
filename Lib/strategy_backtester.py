
class backtest():

    def __init__(self, strategy, plot_results=False):
        self._strategy = strategy
        self.plot_results = False

    def trade(self):
        self._strategy.trade(plot=self.plot_results)

    
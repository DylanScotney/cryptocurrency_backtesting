
class backtest():
    """
    Context class for implementing trading strategies.

    Construction:
    - strategy:             Trading strategy class such as:
                            crossoverTrading, zScoreTrading.
    - plot_results:         bool to indicate whether to plot trading
                            activity.

    Example usage:
    ```
    MA_type = "SMA" # simple moving average
    MAslow = 40 # slow moving average period
    MAfast = 10 # fast MA period

    strategy = crossoverTrading(<asset df>, <asset sym>, MA_type,
                                MAslow, fast_MA=MAfast)
    trader = backtest(strategy)
    trader.trade()
    ```
    """

    def __init__(self, strategy, plot_results=False):
        self._strategy = strategy
        self.plot_results = plot_results

    def trade(self):
        """
        Implements the stategies trading method.

        trade() method of each strategy stores returns in inputted
        df['returns']. See crossover_trading_strategy.py or
        zscore_trading_strategy.py for more details.
        """

        self._strategy.trade(plot=self.plot_results)

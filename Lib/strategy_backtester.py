
class backtest():
    """
    Context class for implementing trading strategies. 
    
    Construction:
    - strategy:             Trading strategy class such as:
                            crossoverTrading, zScoreTrading. 
    - plot_results:         bool to indicate whether to plot trading
                            activity.
    """

    def __init__(self, strategy, plot_results=False):
        self._strategy = strategy
        self.plot_results = plot_results

    def trade(self):
        """
        Implements the stategies trading method. 
        """
        
        self._strategy.trade(plot=self.plot_results)

    
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from pykalman import KalmanFilter

from ..types.zscore import zScore
from ..types.position import Position
from ..types.exponential_moving_average import expMovingAverage


class pairsTrader():
    """
    A class that backtests a mean-reverting strategy on a stationary 
    spread.
    
    Different data is stored in a pandas dataframe.

    Generates a stationary spread between two assets and then
    calculates a zscore of a given period to determine when series will
    revert to mean. 

    Initialisation:
    - x, y:                     (list, floats) price series of two
                                cointegrated assets
    - asset1, asset2:           (str) labels for each price series x, y
    - bandwidth:                (float) bandwidth for zscore logic
    - fee:                      (float) fractional trading fee

    Members:
    - self.name:                (str) name of the spread, used for plots
    - self.xsym, ysym:          (str) name of each series x,y
    - self.spreadPosition:            (Position) custom position object for 
                                handling trade positions.
    - self.trading_fee:         (float) fractional trading fee
    - self.opentimes,
          .closetimes:          (list, int) stores indicies of trade
                                execution times.
    - self.df:                  (pandas Dataframe) stores data for 
                                trading including spread vals, hedge
                                ratio, zscore etc. 
    """

    def __init__(self, x, y, asset1, asset2, zperiod, bandwidth=2.0, fee=0.0):
        self.name = asset1 + "/" + asset2        
        self.xsym, self.ysym = asset1, asset2
        self.spreadPosition = Position()
        self.xPosition = Position()
        self.yPosition = Position()
        self.bw = bandwidth
        self.zperiod = zperiod
        self.trading_fee = fee
        self.opentimes = []
        self.closetimes = []

        self.df = pd.DataFrame({asset1: x, asset2: y})
        self.df['spread'] = 0.0
        self.df['zscore'] = 0.0
        self.df['HR'] = 0.0  # Hedge ratio
        self.df['returns'] = 0.0

        # Use of a moving average to smooth spread
        self.df['xMA'] = expMovingAverage(x, 10).getArray()  
        self.df['yMA'] = expMovingAverage(y, 10).getArray()

    def getSpreadPrice(self, t):
        """
        Gets the value of the spread at index t
        """
        return self.df.loc[t, 'spread']
    
    def getXPrice(self, t):
        """
        Gets the value of the x price series at time t
        """
        return self.df.loc[t, self.xsym]

    def getYPrice(self, t):
        """
        gets the value of the y price series at time t
        """
        return self.df.loc[t, self.ysym]    

    def getHedgeRatio(self, t):
        """
        Gets the value of the hedge ratio at index t
        """
        return self.df.loc[t, 'HR']

    def getZScore(self, t):
        """
        Gets the value of the z score at index t
        """
        return self.df.loc[t, 'zscore']

    def _storeTradeReturns(self, t):
        """
        Stores trade returns from closing a position in index t
        """
        HR = self.getHedgeRatio(t)
        yratio, xratio = 1.0 / (1.0 + HR), HR / (1.0 + HR)

        yreturn = self.yPosition.getTradeReturn()*yratio
        xreturn = self.yPosition.getTradeReturn()*xratio

        self.df.loc[t, 'returns'] = yreturn + xreturn
    
    def openPosition(self, t, pos_type):
        """
        Opens a position at time t.
        """  
        spreadprice = self.getSpreadPrice(t) 
        xspotprice = self.getXPrice(t)
        yspotprice = self.getYPrice(t)   

        if pos_type == 'L':            
            self.spreadPosition.open(spreadprice, 'L', fee=self.trading_fee)
            self.yPosition.open(yspotprice, 'L', fee=self.trading_fee)
            self.xPosition.open(xspotprice, 'S', fee=self.trading_fee)
            self.opentimes.append(t)
        elif pos_type == 'S':            
            self.spreadPosition.open(spreadprice, 'S', fee=self.trading_fee)
            self.yPosition.open(yspotprice, 'S', fee=self.trading_fee)
            self.xPosition.open(xspotprice, 'L', fee=self.trading_fee)
            self.opentimes.append(t)
        else:
            raise ValueError("Position type not recognised")

    def closePosition(self, t):
        """
        closes a position at time t
        """
        spreadprice = self.getSpreadPrice(t) 
        xspotprice = self.getXPrice(t)
        yspotprice = self.getYPrice(t)   

        self.spreadPosition.close(spreadprice, fee=self.trading_fee)
        self.yPosition.close(yspotprice, fee=self.trading_fee)   
        self.xPosition.close(xspotprice, fee=self.trading_fee)                  
        self.closetimes.append(t)
        self._storeTradeReturns(t)


    def _kf_linear_regression(self, x, y, plot=True):
        """
        Uses KalmanFilter to compute linear regression of everypoint of
        a (x, y) dataset.  

        Looking to find params beta, alpha such that:
        y_i = beta * x_i + alpha,  
        for each point x_i, y_i.

        Inputs:
        x, y:                       (pandas Series) containing asset 
                                    price history. 

        Outputs:
        - state_means[:,0]          (list, floats) list of hedge ratios,
                                    beta.


        Brief background of params:
        - We define intial guess for (beta, alpha) = (0, 0) such that the 
        covariance matrix is all ones.

        - To obtain system state we compute: (beta, alpha).(x_i, 1) = y_i
        so the observation matrix (obs_mat) is a column of 1s and xs.
        """

        # Avoid underflow for small prices 
        x*=10000000 
        y*=10000000
        
        delta = 1e-5
        trans_cov = delta / (1 - delta) * np.eye(2) # How much rand walk moves
        obs_mat = np.expand_dims(np.vstack([[x], [np.ones_like(x)]]).T, axis=1)

        # y is 1-dimensional, (alpha, beta) is 2-dimensional
        kf = KalmanFilter(n_dim_obs=1, n_dim_state=2, 
                          initial_state_mean=[0,0],
                          initial_state_covariance=np.ones((2, 2)),
                          transition_matrices=np.eye(2),
                          observation_matrices=obs_mat,
                          observation_covariance=2,
                          transition_covariance=trans_cov)

        # Use the observations y to get running estimates and errors for the state parameters
        state_means, state_cov = kf.filter(y)

        return state_means[:, 0]

    def _generateSpread(self, t0=0, T=None, plot=False):
        """
        Generates spread y - beta*x where y, x are asset series, beta 
        is the hedge ratio. Keeps hedge ratio constant if a position is 
        open.

        Inputs: 
        - t0:                   (int) starting index to generate spread
        - T:                    (int) final index to generate spread
        """
        
        if(T is None):
            T = self.df.shape[0]       
        
        if self.spreadPosition.getPosition() == 0:
            hold_hedge_ratio = False
        else:
            hold_hedge_ratio = True        
        
        if hold_hedge_ratio:            
            # Keep HR const, carry previous value forward.
            t = t0
            while(t <= T):
                self.df.loc[t, 'HR'] = self.df.loc[t-1, 'HR']
                t+=1
        else:
            # Generate hedge ratio using kalman filter
            xMA, yMA = self.df.loc[t0:T, 'xMA'], self.df.loc[t0:T, 'yMA']
            self.df.loc[t0:T, 'HR'] = self._kf_linear_regression(xMA, yMA)
        
        # spread = y - HR*x
        self.df.loc[t0:T, 'spread'] = (self.df.loc[t0:T, self.ysym] 
                                       - self.df.loc[t0:T, self.xsym]
                                       * self.df.loc[t0:T, 'HR'])
        if(plot):
            self.plotSpread(t0=t0, T=T)

    def _generateZScore(self, period, t0=None, T=None):
        """
        Generates zscore of a given period between t0 and T. 

        Note: t0 > period as need atleast period points as a lookback 
        window. 
        """
        if(t0 is None):
            t0 = period
        if(T is None):
            T = self.df.shape[0]

        zscr = zScore(self.df.loc[t0-period:T-1, 'spread'], period).getArray()
        self.df.loc[t0:T, 'zscore'] = zscr.loc[t0:T-1]
    
    def trade(self, plot=False):
        """
        Executes all trades for the pairs trading strategy. 

        Inputs:
        - plot:                (bool) bool to plot trading.
        """
        
        
        t0, T = self.zperiod, self.df.shape[0]-1
        position_t = 0
        self._generateSpread(T=t0)
        self._generateZScore(T=t0, period=self.zperiod)

        for t in range(t0, T):
            
            self._generateSpread(t0=t, T=t+1)
            self._generateZScore(t0=t, T=t+1, period=self.zperiod)

            z_t, z_t_1 = self.getZScore(t), self.getZScore(t-1) 
            position_t = self.spreadPosition.getPosition()

            # Open logic
            #------------------------------------------------------------------
            if (position_t == 0):
                if (z_t > - self.bw) and (z_t_1 < -self.bw) and (z_t < 0):   
                    # Long Spread
                    self.openPosition(t, 'L')
                
                if (z_t < self.bw) and (z_t_1 > self.bw) and (z_t > 0):
                    # Short Spread
                    self.openPosition(t, 'S')
            #------------------------------------------------------------------

            # Close logic
            #------------------------------------------------------------------
            if (position_t == 1):
                if (z_t >= 0) and (z_t_1 < 0):
                    self.closePosition(t)
            
            if (position_t == -1):
                if (z_t <= 0) and (z_t_1  > 0):     
                    self.closePosition(t)
            #------------------------------------------------------------------

        if (plot):
            self.plotTrading(t0=t0, T=T)
        
    def plotSpread(self, t0=0, T=None):
        """
        Plots spread an associated hedge ratio
        """
        if T==None:
            T=self.df.shape[0]

        plt.subplot(311)
        self.df.loc[t0:T, 'spread'].plot()
        plt.plot([t0, T], [0, 0], c='k', ls='--', lw=0.5)
        plt.ylabel(self.name)
        plt.subplot(312)
        self.df.loc[t0:T, 'zscore'].plot()        
        plt.plot([t0, T], [2, 2], c='k', ls='--', lw=0.5)
        plt.plot([t0, T], [-2, -2], c='k', ls='--', lw=0.5)
        plt.ylabel('Z Score')
        plt.subplot(313)       
        self.df.loc[t0:T, 'HR'].plot()
        plt.ylabel("Hedge Ratio")            
        plt.xlabel("Time (hours)")
        plt.show()

    def plotTrading(self,t0=0, T=None):
        """
        Plots all executed trades
        """       
        
        if T==None:
            T=self.df.shape[0]

        plt.subplot(411)
        self.df.loc[t0:T, 'spread'].plot()
        expMovingAverage(self.df.loc[t0:T, 'spread'], self.zperiod).getArray().plot()
        plt.plot([t0, T], [0, 0], c='k', ls='--', lw=0.5)
        plt.ylabel(self.name)
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in self.opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in self.closetimes]

        plt.subplot(412)
        self.df.loc[t0:T, 'zscore'].plot()
        plt.plot([t0, T], [self.bw, self.bw], c='k', ls='--', lw=0.5)
        plt.plot([t0, T], [-self.bw, -self.bw], c='k', ls='--', lw=0.5)
        plt.plot([t0, T], [0, 0], c='k', ls='--', lw=0.5)
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in self.opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in self.closetimes]
        plt.ylabel('Z Score')

        plt.subplot(413)
        self.df.loc[t0:T, 'HR'].plot()
        [plt.axvline(x, c='g', lw=0.5, ls='--') for x in self.opentimes]
        [plt.axvline(x, c='r', lw=0.5, ls='--') for x in self.closetimes]
        plt.ylabel("Hedge Ratio")    

        plt.subplot(414)
        returns = self.df.loc[t0:T, 'returns'].cumsum()*100
        returns.plot()        
        #[plt.axvline(x, c='g', lw=0.5, ls='--') for x in self.opentimes]
        #[plt.axvline(x, c='r', lw=0.5, ls='--') for x in self.closetimes]
        plt.ylabel('Returns (%)')
        plt.xlabel('Hours')
        plt.show()

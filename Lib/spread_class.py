from matplotlib import pyplot as plt
import numpy as np
from pykalman import KalmanFilter

from ..Lib.simple_moving_average_class import simpleMovingAverage


class pairsSpread():

    def __init__(self, df, asset1, asset2):
        self.name = asset2 + "/" + asset1
        self.xsym, self.ysym = asset1, asset2
        self.x = df.loc[:, asset1]
        self.y = df.loc[:, asset2]
        self._spread = np.zeros(len(df.index))
        self._hedge_ratio = np.zeros(len(df.index))

    
    def kf_linear_regression(self, x, y, plot=True):
        """
        Uses Kalman Filter to compute linear regression of everypoint of
        a (x, y) dataset.  

        Looking to find params beta, alpha such that:
        y_i = beta * x_i + alpha,  
        for each point x_i, y_i.

        Inputs:
        x, y:           x,y are a pandas series dataframe containing a list 
                        of asset price history. 


        Brief background of params:
        - We define intial guess for (beta, alpha) = (0, 0) such that the 
        covariance matrix is all ones.

        - To obtain system state we compute: (beta, alpha).(x_i, 1) = y_i
        so the observation matrix (obs_mat) is a column of 1s and xs.
        """

        # Avoid rounding errors for very small valued series
        x*=10000000 
        y*=10000000
        
        delta = 1e-5
        trans_cov = delta / (1 - delta) * np.eye(2) # How much random walk wiggles
        obs_mat = np.expand_dims(np.vstack([[x], [np.ones_like(x)]]).T, axis=1)

        kf = KalmanFilter(n_dim_obs=1, n_dim_state=2, # y is 1-dimensional, (alpha, beta) is 2-dimensional
                          initial_state_mean=[0,0],
                          initial_state_covariance=np.ones((2, 2)),
                          transition_matrices=np.eye(2),
                          observation_matrices=obs_mat,
                          observation_covariance=2,
                          transition_covariance=trans_cov)

        # Use the observations y to get running estimates and errors for the state parameters
        state_means, state_cov = kf.filter(y)
        return state_means[:, 0]

    def generateSpread(self, t0=None, T=None, hold_hedge_ratio=False, plot=False):
        
        if(t0 is None):
            t0 = 0
        if(T is None):
            T = len(self.x)
        
        if(not hold_hedge_ratio):
            period = 20
            xMA = simpleMovingAverage(self.x[t0:T], period).getArray()[period:]
            yMA = simpleMovingAverage(self.y[t0:T], period).getArray()[period:]
            self._hedge_ratio[t0+period:T] = self.kf_linear_regression(xMA, yMA)
        else:
            t = t0
            while(t <= len(T)):
                # Keep HR const, carry previous value forward.
                self._hedge_ratio[t] = self._hedge_ratio[t-1]
                t+=1
            else:
                raise ValueError("Hedge ratio is longer than x")
        
        self._spread[t0:T] = self.y - self.x*self._hedge_ratio

        if(plot):
            plt.subplot(411)
            plt.plot(self.x[period:], c='r')
            plt.ylabel(self.xsym+"/BTC")
            
            plt.subplot(412)
            plt.plot(self.y[period:], c='g')
            plt.ylabel(self.ysym+"/BTC")

            plt.subplot(413)
            plt.plot(self._spread[period:])
            plt.ylabel(self.name)

            plt.subplot(414)
            plt.plot(self._hedge_ratio[period:])
            plt.ylabel("Hedge Ratio")            
            plt.xlabel("Time (hours)")
            plt.show()
        
        


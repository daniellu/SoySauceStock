import datetime
import pandas as pd


class TechnicalAnalyzer(object):
    def __init__(self):
        pass

    @staticmethod
    def moving_average_convergence(df, nslow=26, nfast=12, nsignal=9):
        slow_ema = pd.ewma(df, span=nslow)
        fast_ema = pd.ewma(df, span=nfast)
        macd_line = fast_ema - slow_ema
        signal_line = pd.ewma(macd_line, span=nsignal)
        histogram = macd_line - signal_line
        return histogram, macd_line, signal_line,  slow_ema, fast_ema

    @staticmethod
    def target_macd_h_price(s, target_price=None):
        if target_price is None:
            target_price = s.iloc[-1]
        new_series = s.append(pd.Series(target_price, index={'9999-12-31'})).copy()

        h,_,_,_,_ = TechnicalAnalyzer.moving_average_convergence(new_series)

        for iloop in range(0, 1000):
            h,_,_,_,_ = TechnicalAnalyzer.moving_average_convergence(new_series)

            if abs(h.iloc[-2] - h.iloc[-1]) < 0.0001:
                break
            if h.iloc[-2] > h.iloc[-1]:
                target_price += 0.01
            if h.iloc[-2] < h.iloc[-1]:
                target_price -= 0.01
            new_series.iloc[-1] = target_price
        # print('MACD-H: ' + str(h.iloc[-1]))
        return target_price
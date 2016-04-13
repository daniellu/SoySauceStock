import pandas as pd
import json
import os
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta
from soysaucestock.technical_analyzer import  TechnicalAnalyzer


def add_years(date_str, num):
    d = parser.parse(date_str).date()
    return str(d + relativedelta(years=num))


def add_days(date_str, num):
    d = parser.parse(date_str).date()
    return str(d + relativedelta(days=num))


class StockChartTester(object):
    def __init__(self, json_file_path='C:\\Tools\\stockchart.json'):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)  # seconds
        self.driver.get("http://stockcharts.com")

        with open(json_file_path) as data_file:
            account_info = json.load(data_file)
        self.driver.find_element_by_link_text('Login').click()
        self.driver.find_element_by_id('form_UserID').send_keys(account_info['user_name'])
        self.driver.find_element_by_name('form_UserPassword').send_keys(account_info['password'])
        self.driver.find_element_by_id('loginbutton').submit()

    def move_next(self, df):
        ticker = df.iloc[0].Ticker
        start_period = df.iloc[0].Date
        self.show_stock(ticker, start_period)
        print(str.format('Ticker: {0}\nDate: {1}', ticker, start_period))

    def show_stock(self, ticker, start_period):
        one_year_back = add_years(start_period, -1)
        self.driver.find_element_by_id('navsearchtext').send_keys(Keys.CONTROL + 'a' + Keys.NULL,ticker)
        self.driver.find_element_by_id('navsearchbutton').click()
        select = Select(self.driver.find_element_by_id('dataRange'))
        select.select_by_visible_text('Select Start/End')
        self.driver.find_element_by_id('start').send_keys(Keys.CONTROL + 'a' + Keys.NULL,one_year_back)
        self.driver.find_element_by_id('submitButton').click() # otherwise the end date wont change
        self.driver.find_element_by_id('end').send_keys(Keys.CONTROL + 'a' + Keys.NULL, start_period)
        self.driver.find_element_by_id('submitButton').click()

    def save_chart(self, trade, dest='bull'):
        ticker = trade.EnterTicker
        file_period_name = trade.EnterDate.replace('-','_')
        enter_period = trade.EnterDate
        enter_one_year_back = add_years(enter_period, -1)
        enter_file_name = os.path.join(dest, str.format('{0}_{1}_Entry.png', file_period_name, ticker.replace('/', '-')))
        exit_period = trade.ExitDate
        exit_one_year_back = add_years(exit_period, -1)
        exit_file_name = os.path.join(dest, str.format('{0}_{1}_Exit.png', file_period_name, ticker.replace('/', '-')))
        p10_period = add_days(exit_period, 15) # two weeks
        p10_one_year_back = add_years(p10_period, -1)
        p10_file_name = os.path.join(dest, str.format('{0}_{1}_Exit_p10.png', file_period_name, ticker.replace('/', '-')))
        p30_period = add_days(exit_period, 90) # three months
        p30_one_year_back = add_years(p30_period, -1)
        p30_file_name = os.path.join(dest, str.format('{0}_{1}_Exit_p30.png', file_period_name, ticker.replace('/', '-')))
        self.save_pic(ticker, enter_one_year_back, enter_period, enter_file_name)
        self.save_pic(ticker, exit_one_year_back, exit_period, exit_file_name)
        self.save_pic(ticker, p10_one_year_back, p10_period, p10_file_name)
        self.save_pic(ticker, p30_one_year_back, p30_period, p30_file_name)

    def save_pic(self, ticker, start_date, end_date, file_name):
        self.driver.find_element_by_id('navsearchtext').send_keys(Keys.CONTROL + 'a' + Keys.NULL, ticker)
        self.driver.find_element_by_id('navsearchbutton').click()
        select = Select(self.driver.find_element_by_id('dataRange'))
        select.select_by_visible_text('Select Start/End')
        self.driver.find_element_by_id('start').send_keys(Keys.CONTROL + 'a' + Keys.NULL, start_date)
        self.driver.find_element_by_id('submitButton').click() # otherwise the end date wont change
        self.driver.find_element_by_id('end').send_keys(Keys.CONTROL + 'a' + Keys.NULL, end_date)
        self.driver.find_element_by_id('submitButton').click()
        self.driver.get_screenshot_as_file(file_name)

    def get_driver(self):
        return self.driver

    @staticmethod
    def remove_candidate_if_traded(candidate_df, trade_df):
        if trade_df.empty or (any(trade_df.EnterTicker == candidate_df.iloc[0].Ticker) and trade_df.loc[trade_df.EnterTicker == candidate_df.iloc[0].Ticker].ExitDate.max() > candidate_df.iloc[0].Date):
            candidate_df.drop(candidate_df.head(1).index, inplace=True)
            StockChartTester.remove_candidate_if_traded(candidate_df, trade_df)

    @staticmethod
    def process_macd_calc_short(ticker, screen_date, price_dest='C:\\temp'):
        #first load the price
        price_df = pd.read_csv(os.path.join(price_dest, str.format('{0}.csv', ticker.replace('/','-'))) , index_col=0)
        date_list = price_df.index.tolist()
        curr_index = price_df.index.get_loc(screen_date)

        entry_price = 0
        init_stop = 0

        for i in range(0,10):
            market_date = date_list[curr_index + 1 + i]
            macd_price = TechnicalAnalyzer.target_macd_h_price(price_df.ix[:curr_index + 1 + i].Close)
            close_price = price_df.ix[market_date].Close

            if close_price <= macd_price:
                entry_price = close_price
                enter_date = market_date
                init_stop = price_df[:enter_date].tail(5).High.max()
                break

        # if the entry price is still 0, that means no entry after 10 days, mark this trade and leave
        if entry_price == 0:
            return TradeResult(enter_date=screen_date,
                               enter_ticker=ticker,
                               enter_price=0,
                               initial_stop=0,
                               target_price=0,
                               enter_direction='SHORT',
                               exit_date=screen_date,
                               exit_price=0,
                               is_missed=1)

        curr_index = price_df.index.get_loc(enter_date)

        # exit rule, if hit MACD price, close
        # if close hits > 1R + init_stop, move price to enter plus 2 cents
        # if close hits > 2R + init_stop, move price to 1R
        # if close hits > 3R + init_stop, move price to close
        # if after 10 days no move, then close position on end of day

        # we enter on close, so that day is effectively safe, we focus on the next day
        r = abs(init_stop - entry_price)
        stop_price = init_stop
        exit_price = 0
        for i in range(0,10):
            market_date = date_list[curr_index + 1 + i]
            today_open = price_df.ix[market_date].Open
            today_close = price_df.ix[market_date].Close
            today_high = price_df.ix[market_date].High
            today_low = price_df.ix[market_date].Low
            exec_price = StockChartTester._get_short_trade_price(stop_price, today_open, today_close, today_high,
                                                                 today_low)
            #print(str.format('{0}, open:{1}, close{2}, high:{3}, low{4}, stop:{5}, exec: {6}', market_date,
            #                 today_open, today_close, today_high, today_low, stop_price, exec_price))
            if exec_price is not None:
                exit_date = market_date
                exit_price = exec_price
                break

            if entry_price - today_close > 4 * r:
                exit_date = market_date
                exit_price = today_close
                break

            # move stops if get some profit
            if entry_price - close_price > r:
                stop_price = entry_price - 0.02
            if entry_price - close_price > 2 * r:
                stop_price = entry_price - 1 * r
            if entry_price - close_price > 3 * r:
                stop_price = entry_price - 2 * r

        if exit_price == 0:
            exit_date = market_date
            exit_price = today_close

        return TradeResult(enter_date=enter_date,
                           enter_ticker=ticker,
                           enter_price=entry_price,
                           initial_stop=init_stop,
                           target_price=entry_price - 3 * (init_stop - entry_price),
                           enter_direction='SHORT',
                           exit_date=exit_date,
                           exit_price=exit_price,
                           is_missed=0)

    @staticmethod
    def process_macd_calc_long(ticker, screen_date, price_dest='C:\\temp'):
        #first load the price
        price_df = pd.read_csv(os.path.join(price_dest, str.format('{0}.csv', ticker.replace('/', '-'))) , index_col=0)
        date_list = price_df.index.tolist()
        curr_index = price_df.index.get_loc(screen_date)

        entry_price = 0
        init_stop = 0

        for i in range(0, 10):
            market_date = date_list[curr_index + 1 + i]
            macd_price = TechnicalAnalyzer.target_macd_h_price(price_df.ix[:curr_index + 1 + i].Close)
            close_price = price_df.ix[market_date].Close

            if close_price >= macd_price:
                entry_price = close_price
                enter_date = market_date
                init_stop = price_df[:enter_date].tail().Low.min()
                break

        # if the entry price is still 0, that means no entry after 10 days, mark this trade and leave
        if entry_price == 0:
            return TradeResult(enter_date=screen_date,
                               enter_ticker=ticker,
                               enter_price=0,
                               initial_stop=0,
                               target_price=0,
                               enter_direction='Long',
                               exit_date=screen_date,
                               exit_price=0,
                               is_missed=1)

        curr_index = price_df.index.get_loc(enter_date)

        # exit rule, if hit MACD price, close
        # if close hits > init_stop - 1R, move price to enter plus 2 cents
        # if close hits > init_stop - 2R, move price to 1R
        # if close hits > init_stop - 3R, move price to close
        # if after 10 days no move, then close position on end of day

        # we enter on close, so that day is effectively safe, we focus on the next day
        r = abs(init_stop - entry_price)
        stop_price = init_stop
        exit_price = 0
        for i in range(0, 10):
            market_date = date_list[curr_index + 1 + i]
            today_open = price_df.ix[market_date].Open
            today_close = price_df.ix[market_date].Close
            today_high = price_df.ix[market_date].High
            today_low = price_df.ix[market_date].Low
            exec_price = StockChartTester._get_long_trade_price(stop_price, today_open, today_close, today_high,
                                                                 today_low)
            # print(str.format('{0}, open:{1}, close{2}, high:{3}, low{4}, stop:{5}, exec: {6}', market_date,
            #                  today_open, today_close, today_high, today_low, stop_price, exec_price))
            if exec_price is not None:
                exit_date = market_date
                exit_price = exec_price
                break

            if today_close - entry_price > 4 * r:
                exit_date = market_date
                exit_price = today_close
                break

            # move stops if get some profit
            if close_price - entry_price > r:
                stop_price = entry_price + 0.02
            if close_price - entry_price > 2 * r:
                stop_price = entry_price + 1 * r
            if close_price - entry_price > 3 * r:
                stop_price = entry_price + 2 * r

        if exit_price == 0:
            exit_date = market_date
            exit_price = today_close

        return TradeResult(enter_date=enter_date,
                           enter_ticker=ticker,
                           enter_price=entry_price,
                           initial_stop=init_stop,
                           target_price=entry_price + 3 * (entry_price - init_stop),
                           enter_direction='Long',
                           exit_date=exit_date,
                           exit_price=exit_price,
                           is_missed=0)

    @staticmethod
    def _get_short_trade_price(stop, price_open, price_close, price_high, price_low, is_gtc=False):
        if stop > price_high and is_gtc:
            return price_close

        if stop > price_high:
            return None

        # gap up open, exit at market open
        if stop < price_open:
            return price_open

        if price_low <= stop <= price_high:
            return stop

        raise Exception(stop, price_open, price_close, price_high, price_low)

    @staticmethod
    def _get_long_trade_price(stop, price_open, price_close, price_high, price_low, is_gtc=False):
        if stop < price_low and is_gtc:
            return price_close

        if stop < price_low:
            return None

        # gap down open, exit at market open
        if stop > price_open:
            return price_open

        if price_low <= stop <= price_high:
            return stop

        raise Exception(stop, price_open, price_close, price_high, price_low)

class TradeResult(object):
    def __init__(self, enter_date, enter_ticker, enter_price, initial_stop, target_price, enter_direction, exit_date,
                 exit_price, is_missed):
        self.enter_date = enter_date
        self.enter_ticker = enter_ticker
        self.enter_price = enter_price
        self.initial_stop = initial_stop
        self.target_price = target_price
        self.enter_direction = enter_direction
        self.exit_date = exit_date
        self.exit_price = exit_price
        self.is_missed = is_missed

    def todf(self):
        return pd.DataFrame({
                "EnterDate": self.enter_date,
                "EnterTicker": self.enter_ticker,
                "EnterPrice": self.enter_price,
                "InitialStop": self.initial_stop,
                "TargetPrice": self.target_price,
                "EnterDirection": self.enter_direction,
                "ExitDate": self.exit_date,
                "ExitPrice": self.exit_price,
                "IsMissed": self.is_missed
            }, index=[0])

    def tostr(self):
        print(str.format(
                "EnterDate: {0} \tEnterTicker: {1}\nEnterPrice: {2} \t\tInitialStop: {3}\nTargetPrice: {4}\tEnterDirection: {5}\nExitDate: {6}\tExitPrice: {7} IsMissed: {8}"
                ,self.enter_date
                ,self.enter_ticker
                ,self.enter_price
                ,self.initial_stop
                ,self.target_price
                ,self.enter_direction
                ,self.exit_date
                ,self.exit_price
                ,self.is_missed
            ) )
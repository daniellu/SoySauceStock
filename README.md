# SoySauceStock
SoySauceStock is the attempt to provide data, research and back test framework for stock trading.
It will cover swing trading testing for Canadian and US stocks.

## Data
Stock data is scraped from StockCharts.com, note that you need to have an account to access the data.
The data is stored in a HDF5 file based database, it is designed to reload the data on every run.

## Back testing
Back testing consumes the historical data and will follow the event driven back testing framework to verify
the strategy. I am also in favor of simulation to stress testing the data.

## Research
To prototyping a strategy, a common api module is provided for ipython notebook


# EMATrading

The project contains the following files.

```
project
│   data.csv
│   main_multi.py
│   main_single.py
│   README.md
```

## Prerequisites
The framework is built on [Python3.7](https://www.python.org/downloads/release/python-3713/), and relies on the following dependencies.
* [`backtrader`](https://www.backtrader.com)
* `datetime`
* `os`
* `pandas`
* `sys`

## Preprocess
All stocks are scanned and only the ones starting from '2013-01-04' and ending at '2021-03-19' are kept.

## Single stock
The strategy is a combination of SMA and MACD. Only the first stock after preprocessing is fed to backtest. Run
```
python main_single.py
```

## Multiple stocks
The strategy is simply MACD. The first five (can be larger) stocks after preprocessing are fed to backtest. Run
```
python main_multi.py
```
Remark: Due to time limit, the trading size is fixed to 10. Therefore, many orders may not succeed when there are too many stocks.
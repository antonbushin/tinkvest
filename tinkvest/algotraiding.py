"""Методы алготрейдинга для реализации торгового робота"""

import asyncio
import pandas as pd
import yfinance as yf
import mplfinance as mpf
from datetime import datetime
import pathlib
from tinkvest.settings import HERE
from tinkvest.utils import prepare_filename


def ti_search_by_ticker(ticker: str) -> pd.DataFrame:
    df = yf.download(tickers=ticker,
                     period="1mo",
                     interval="1h",
                     auto_adjust=True)
    return df


# df.ta.sma(length=20, append=True)
def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    df.ta.bbands(window=4, window_dev=20, append=True)
    df["ema12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["ema26"] = df["Close"].ewm(span=26, adjust=False).mean()
    df["macd"] = df["ema12"] - df["ema26"]
    df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["histogram"] = df["macd"] - df["signal"]
    return df


def generate_add_plots(df: pd.DataFrame, start_date: str) -> list:
    lower_b = df.loc[start_date:, ["BBL_5_2.0"]]
    upper_b = df.loc[start_date:, ["BBU_5_2.0"]]
    ema12 = df.loc[start_date:, ["ema12"]]
    ema26 = df.loc[start_date:, ["ema26"]]
    histogram = df.loc[start_date:, ["histogram"]]
    macd = df.loc[start_date:, ["macd"]]
    signal = df.loc[start_date:, ["signal"]]

    add_plots = [mpf.make_addplot(upper_b, linestyle="dashdot", color="g"),
                 mpf.make_addplot(lower_b, linestyle="dashdot", color="r"),
                 mpf.make_addplot(ema12, color="lime"),
                 mpf.make_addplot(ema26, color="b"),
                 mpf.make_addplot(histogram, type="bar", width=0.7, panel=1,
                                  color="dimgray", alpha=1, secondary_y=False),
                 mpf.make_addplot(macd, panel=1, color="b", secondary_y=True),
                 mpf.make_addplot(signal, panel=1, color="r", secondary_y=True), ]
    return add_plots


def prepare_plot(df: pd.DataFrame, start_date: str, add_plots: list, title: str) -> str:
    print("HERE:", HERE)
    pathlib.Path(f"{HERE}/resources/images/").mkdir(parents=True, exist_ok=True)
    filename = f"{HERE}/resources/images/" + title + "_" + datetime.now().strftime("%d.%m.%Y %H:%M:%S") + ".png"
    filename = prepare_filename(filename)
    print("filename:", filename)
    mpf.plot(data=df[start_date:],
             type="candle",
             addplot=add_plots,
             # mav=(10, 20),
             volume=True,
             figscale=2,
             figratio=(10, 6),
             title=title,
             tight_layout=True,
             style="classic",
             volume_panel=2,
             panel_ratios=(6, 3, 2),
             savefig=filename)
    return filename


async def get_plot(ticker: str) -> str:
    start_date = "2021-12-01"
    ticker_data = ti_search_by_ticker(ticker=ticker)
    df = prepare_df(df=ticker_data)
    add_plots = generate_add_plots(df=df, start_date=start_date)
    await asyncio.sleep(1)
    filename = prepare_plot(df=df, start_date=start_date, add_plots=add_plots, title=ticker)
    return filename

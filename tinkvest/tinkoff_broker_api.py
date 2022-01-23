"""Реализация API брокера Тинькофф"""

from typing import List, Optional
from pydantic import BaseModel
import tinvest
from tinvest import MarketInstrument
from project_secrets.tokens import TINKOFF_SANDBOX_TOKEN
from tinkvest.utils.logger import logger

logger = logger(__name__)


class TinkoffData(BaseModel):
    """Хранение данных торговой сессии"""
    instruments: Optional[List[MarketInstrument]] = []
    stocks: Optional[List[MarketInstrument]] = []
    candles: Optional[List[MarketInstrument]] = []


session_data = TinkoffData()
client = tinvest.AsyncClient(token=TINKOFF_SANDBOX_TOKEN, use_sandbox=True)


async def ti_search_by_ticker(ticker: str):
    """Поиск информации о тикере"""
    result = await client.get_market_search_by_ticker(ticker=ticker)
    session_data.instruments.extend(result.payload.instruments)
    session_data.instruments = {v.figi: v for v in session_data.instruments}.values()


async def ti_get_instruments():
    """Загрузка данных по акциям, фондам, бондам и валюте"""
    result = session_data.instruments

    stocks = await client.get_market_stocks()
    result.extend(stocks.payload.instruments)
    etfs = await client.get_market_etfs()
    result.extend(etfs.payload.instruments)
    bonds = await client.get_market_bonds()
    result.extend(bonds.payload.instruments)
    currencies = await client.get_market_currencies()
    result.extend(currencies.payload.instruments)

    result = {v.figi: v for v in result}.values()
    result = sorted(result, key=lambda d: d.ticker)
    session_data.instruments = result
    logger.info("instruments len: %s", len(session_data.instruments))

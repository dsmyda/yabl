import asyncio
from asyncio.log import logger
from os import getenv
from binance import AsyncClient
from core import SourceNode


class BinanceHistoricalSourceNode(SourceNode):
    """ Pulls historical Kline data from the Binance API and feeds it into a data source """

    KLINE_COLUMNS = ["Open_Time", "Open", "High", "Low", "Close", "Volume", "Close_Time", "Quote_Asset_Volume",
                     "Number_of_Trades", "Taker_Buy_Base_Asset_Volume", "Taker_Buy_Quote_Asset_Volume"]

    def __init__(self, config):
        super().__init__(config)

    async def produce(self):
        logger.debug('[' + self.__class__.__name__ + '] preparing to initialize client')
        client = await AsyncClient.create(getenv('BINANCE_API_KEY'), getenv('BINANCE_API_SECRET'), tld='us')
        logger.debug('[' + self.__class__.__name__ + '] finished initializing client')

        try:
            logger.debug('[' + self.__class__.__name__ + '] preparing to fetch kline data')
            for kline in await client.get_historical_klines(self.config['pair'], self.config['timeframe'],
                                                            self.config['start'], limit=1000):
                logger.debug('[' + self.__class__.__name__ + '] kline data received')
                kline.pop()  # Pop off legacy field, which we can ignore
                yield dict(zip(BinanceHistoricalSourceNode.KLINE_COLUMNS, [[float(v) if i > 0 else v] for i, v in enumerate(kline)]))

            logger.debug('[' + self.__class__.__name__ + '] finished fetching kline data')
        finally:
            logger.debug('[' + self.__class__.__name__ + '] preparing to close connection')
            await client.close_connection()
            logger.debug('[' + self.__class__.__name__ + '] finishing closing connection')

        yield None

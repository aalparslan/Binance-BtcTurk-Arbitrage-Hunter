import asyncio
import re
from binance import Client,  AsyncClient, BinanceSocketManager
import time
import pandas as pd
import nest_asyncio

class BinanceObj:
    def __init__(self, conn) -> None:
        self.parent_conn = conn    
        nest_asyncio.apply()


    async def main(self):
        client = await AsyncClient.create()
        bm = BinanceSocketManager(client)
        # start any sockets here, i.e a trade socket
        ts = bm.symbol_book_ticker_socket('LUNABUSD')
        # then start receiving messages``
        async with ts as tscm:
            while True:
                res = await tscm.recv()
                self.binance_dict = {'ask': res['a'], 'bid': res['b']}
                self.parent_conn.send(self.binance_dict)
                # print(self.binance_dict)

        await client.close_connection()

    def get_binance_dict(self):
        return self.binance_dict


def run(conn):
    biannceObj = BinanceObj(conn=conn)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(biannceObj.main()) 


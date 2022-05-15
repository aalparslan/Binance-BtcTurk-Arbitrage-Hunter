import asyncio
import base64
import hashlib
import hmac
import json
import time
import websockets


class InterfaceWS:
    def __init__(self, conn, exchange_name: str = None) -> None:
        self.exchange_name = "BTC Turk"
        self.uri = "wss://ws-feed-pro.btcturk.com/"
        self.parent_conn = conn

    async def authenticate_ws(self) -> bool:
        self.ws = await websockets.connect(self.uri)
        publicKey = "";
        privateKey = "";
        nonce = 3000
        print("\nnonce", nonce)
        baseString = "{}{}".format(publicKey, nonce).encode("utf-8")
        print("\nbaseString", baseString)
        signature = hmac.new(
            base64.b64decode(privateKey), baseString, hashlib.sha256
        ).digest()
        print("\nsignature", signature)
        signature = base64.b64encode(signature)
        print("\nsignature", signature)
        timestamp = round(time.time() * 1000)
        print("\ntimestamp", timestamp)
        hmacMessageObject = [
            114,
            {
                "nonce": nonce,
                "publicKey": publicKey,
                "signature": signature.decode("utf-8"),
                "timestamp": timestamp,
                "type": 114,
            },
        ]
        print("hmacMessageObject", hmacMessageObject)
        await self.ws.send(json.dumps(hmacMessageObject))
        while True:
            try:
                response = await asyncio.wait_for(self.ws.recv(), timeout=0.5)
                print("response after auth: ", response)
            except Exception as e:
                print(e)
                break         

    
    async def subscribe_single_trade(self, trade_pair: str) -> None:
        message = [
                    151,
                    {
                        "type": 151,
                        "channel": 'orderbook',
                        "event": trade_pair,
                        "join": True
                    }
                ]    
        await self.ws.send(json.dumps(message))
        while True:
            try:
                response = await asyncio.wait_for(self.ws.recv(), timeout=0.5)
                response = json.loads(response)
                self.btcturk_dict = {'ask':response[1]['AO'][0]['P'], 'bid': response[1]['BO'][0]['P']}
                self.parent_conn.send(self.btcturk_dict)

            except Exception as e:
                pass
    
    def get_btcturk_dict(self):
        return self.btcturk_dict       

async def main(conn):
    w = InterfaceWS(conn=conn)
    await w.authenticate_ws()
    await w.subscribe_single_trade('LUNAUSDT')


def run(conn):
    asyncio.run(main(conn=conn))


    
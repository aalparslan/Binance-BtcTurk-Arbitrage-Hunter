import binanceretrieve
import btcretrieve
from multiprocessing import Process, Pipe
import threading
class ArbitrageHunter:
    min_profitability_ratio = 2.0/1000
    def __init__(self) -> None:
        self.parent_conn_btcturk, self.child_conn_btcturk = Pipe()
        self.parent_conn_binance, self.child_conn_binance = Pipe()
        self.binance_dict = {}
        self.btcturk_dict = {}
        

    def run_binance(self):
        self.p_binance = Process(target=binanceretrieve.run, args=(self.child_conn_binance,))
        self.p_binance.start()

    def run_btcturk(self):
        self.p_btcturk = Process(target=btcretrieve.run, args=(self.child_conn_btcturk,))
        self.p_btcturk.start()
        
    def receive_binance(self):
        while True:
            self.binance_dict = self.parent_conn_binance.recv()

    def receive_btcturk(self):
        while True:
            self.btcturk_dict = self.parent_conn_btcturk.recv()
    
    def receive(self):
        t1 = threading.Thread(target=self.receive_binance)
        t2 = threading.Thread(target=self.receive_btcturk)
        t1.start()
        t2.start()
    
    def get_btcturk_dict(self):
        return self.btcturk_dict

    def get_binance_dict(self):
        return self.binance_dict

    def is_profitable(self, buy_price, sell_price):
        buy_price = int(buy_price.replace('.', ''))
        sell_price = int(sell_price.replace('.', ''))
        len_buy_price = len(str(buy_price))
        len_sell_price = len(str(sell_price))
        if (len_buy_price > len_sell_price):
            sell_price *= 10**(len_buy_price - len_sell_price)
        else:
            buy_price *= 10**(len_sell_price - len_buy_price)

        #remove blow line!
        if(len(str(buy_price)) != len(str(sell_price))):
            print('Error in len of len_buy_price or len_buy_price')

        profit_ratio = ((sell_price - buy_price))/(buy_price*1.0)
        if (profit_ratio > self.min_profitability_ratio):
            print(f"{profit_ratio*100}% profitable")
            return True
        # print(f"{profit_ratio*100}% profitable")
        return False
    
    def hunt(self):
        while True:
            try:
                if (self.btcturk_dict.get('bid') > self.binance_dict.get('ask')):
                    if (self.is_profitable(self.binance_dict.get('ask'), self.btcturk_dict.get('bid'))):
                        print(f"buy from binance at {self.binance_dict['ask']} and sell to btcturk at {self.btcturk_dict['bid']}")
                if (self.btcturk_dict.get('ask') < self.binance_dict.get('bid')):
                    if(self.is_profitable(self.btcturk_dict.get('ask'), self.binance_dict.get('bid'))):
                        print(f"buy from btcturk at {self.btcturk_dict['ask']} and sell to binance at {self.binance_dict['bid']}")  

            except Exception as e:
                print(e)

if __name__ == "__main__":
    arbitrage_hunter = ArbitrageHunter()
    arbitrage_hunter.run_btcturk()
    arbitrage_hunter.run_binance()
    arbitrage_hunter.receive()
    arbitrage_hunter.hunt()
    

    
        
    

    
    
    


        
    
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

import pandas as pd
import time
from datetime import datetime
from functools import reduce

class APIwrapper: 
    
    def __init__(self):
        self.socket = CoinGeckoAPI()
                
    def coin_api(self, tries, delay, backoff, *args): 
        for n in range(tries):
            try: 
                return self.socket.get_coin_market_chart_range_by_id(*args)
            
            except (KeyboardInterrupt, SystemExit):
                raise
                
            except Exception as e:
                time.sleep(delay)
                delay *= backoff
                print(f"{e} occurred. New attempt in {delay} seconds")
                continue 
            
        raise NameError(f"Failed within {tries} attempts")


def get_coins_name_id(dataframe_coin):
    coin_ids = dataframe_coin['id']
    coin_names = dataframe_coin['name']
    
    return coin_ids, coin_names

def create_dataframe(coin, coin_id, minimum_date, maximum_date):
    
    dataframe = []
    timeseries = []
    names = [key for key, val in coin.items()]
    
    for i in range([len(val) for key, val in coin.items()][0]):
        try: 
            variables = [item[i][1] for item in coin.values()]
            date = [datetime.fromtimestamp(item[i][0]/1000).strftime("%Y-%m-%d") for item in coin.values()][0]
            dataframe.append(variables)
            timeseries.append(date)
            minimum_date.append(min(timeseries))
            maximum_date.append(max(timeseries))
        
        except (KeyboardInterrupt, SystemExit):
                raise
        
        except Exception as e:
            time.sleep(10)
            print(f"Error: {e}, occurred for {coin_id}. New attempt in 5 seconds.")
            continue 
    
    dataframe = pd.DataFrame(dataframe, columns = names)
    dataframe["Datetime"] = timeseries
    dataframe["Datetime"] = pd.to_datetime(dataframe["Datetime"])
    dataframe["Id"] = coin_id
    dataframe = dataframe.set_index(["Datetime","Id"])
    
    return minimum_date, maximum_date, timeseries, dataframe

def get_df_by_coin_time_range_to_csv(coin_ids, n_start = 0, n_end = 10, 
                              from_time = '1522195200', to_time = '1575158400', Save = False):

    frames = []
    minim_date = []
    maxim_date = []
    id_coin = []
    
    for coin in coin_ids[n_start : n_end]:
   
        api = APIwrapper()
        tmp = api.coin_api(10, 1, 2, coin,'usd', from_time, to_time)
            
        if [val for key, val in tmp.items()][0] == []:
            continue
        else: 
            id_coin.append(coin) 
        
        minim_date, maxim_date, t, dataframe = create_dataframe(tmp, coin, minim_date, maxim_date) 
    
        if Save == True:
            dataframe.to_csv(coin) 
            print(f"{coin} correctly saved.")
            frames.append(dataframe)
            
        else:
            frames.append(dataframe)
        
        time.sleep(5)
        
    return frames, minim_date, maxim_date, id_coin


def main():
    
    api = APIwrapper()
    coinlist_df = pd.DataFrame(api.socket.get_coins_list())
    coin_ids, coin_names = get_coins_name_id(coinlist_df)
    
    frames = []
    minim_date = []
    maxim_date = []
    id_coin = []
    
    frames, minim_date, maxim_date, id_coin = get_df_by_coin_time_range_to_csv(coin_ids, n_start = 0, n_end = len(coin_ids), 
                                                                               from_time = '1357041600', Save = True)
    
    if minim_date == []:
        print("Coins data available only on minutely/hourly basis. Try with another sequence.")
        
    else:
        index = pd.MultiIndex.from_product([pd.date_range(start= min(minim_date), end=max(maxim_date)).tolist(), 
                                        id_coin], names =['Datetime', 'Id'])  
        match_df = pd.DataFrame(index = index)
        filter_type_frames = match_df.merge(reduce(lambda left,right: pd.concat( [left, right]), frames), how="outer", 
                                    left_index=True, right_index=True).fillna(0)
    
        filter_type_frames.to_csv("test.csv")


if __name__== "__main__":
  main()


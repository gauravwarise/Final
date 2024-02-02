from connectToAPI import ConnectToAPI
import pickle
import json
import time
import asyncio
import websockets
from utils import *
import math

from threading import Thread
import queue

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import sys
import multiprocessing


baseURL="http://127.0.0.1:1234"
wsURL="ws://127.0.0.1:1234"

class StockDetail(ConnectToAPI):
    def __init__(self):
        super().__init__()

        self.flag = 1
        self._pickleFile = "session.pkl"
        self._sessionData = None

        self.stockpicker = []

        try :
            with open(self._pickleFile,"rb") as file :
                self._sessionData = pickle.load(file)    
        except Exception as e:
            print("while reading pickle",e)

        data = {
            "username": "microservice",
            "password": '12345678',
            "role":"microservice",
            "loginURL": baseURL+"/account/login/",
            "wsURL": wsURL+"/ws/stock/"
        }
        if self._login(data):
            asyncio.run(self.connect_to_websocket())
        else:
            print("Login failed. WebSocket connection not established.")

    # async def send_to_websocket_group(self, message):
    #     try:
    #         sessionid = self._sessionData.sessionid
    #         csrf = self._sessionData.csrf
    #     except Exception as e:
    #         print(e)

    #     headers = {"Cookie": f"csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}"}

    #     async with websockets.connect(self._wsURL, extra_headers=headers) as websocket:
    #         data_to_send = json.dumps({"message": message})
    #         await websocket.send(data_to_send)
    #         print(f"Sent to WebSocket Group: {data_to_send}")

    async def receive_stock_list(self,websocket):
        try:
            stocklist = await websocket.recv()
            stocklist_dict = json.loads(stocklist)
            
            result = stocklist_dict.get('message')
            for i in result:
                self.stockpicker.append(i)
            print(f"Received:***************************************************************>{self.stockpicker}")
        except asyncio.TimeoutError:
            print("No message received in the last 5 seconds.")
     
    async def connect_to_websocket(self):
        try:
            sessionid=self._sessionData.sessionid
            csrf=self._sessionData.csrf
            print(sessionid, csrf)
        except Exception as e:
            print(e)
        headers = {"Cookie": f"csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}"}
        async with websockets.connect(self._wsURL,extra_headers=headers) as websocket:
            # try:
            #     stocklist = await websocket.recv()
            #     stocklist_dict = json.loads(stocklist)
                
            #     stockpicker = stocklist_dict.get('message')
            #     print(f"Received:***************************************************************>{stockpicker}")
            # except asyncio.TimeoutError:
            #     print("No message received in the last 5 seconds.")

            p = multiprocessing.Process(target=self.receive_stock_list, args=(websocket,))
            p.start()
            p.join()

            
            if len(self.stockpicker)>0:
            #     c = 0
                while self.flag>0:
                    # stockpicker = ['ADANIENT.NS', 'APOLLOHOSP.NS', 'BAJAJ-AUTO.NS']
                    # try:
                    #     stocklist = await websocket.recv()
                    #     stocklist_dict = json.loads(stocklist)
                        
                    #     stockpicker = stocklist_dict.get('message')
                    #     print(f"Received:***************************************************************>{stockpicker}")
                    # except asyncio.TimeoutError:
                    #     print("No message received in the last 5 seconds.")
                    data ={}
                    n_threads = len(self.stockpicker)
                    thread_list = []
                    que = queue.Queue()

                    for i in range(n_threads):
                        thread = Thread(target=lambda q, arg1: q.put({self.stockpicker[i]: get_quote_table(arg1)}), args=(que, self.stockpicker[i]))
                        thread_list.append(thread)
                        thread_list[i].start()
                    
                    for thread in thread_list:
                        thread.join()
                    
                    while not que.empty():
                        result = que.get()
                        data.update(result)
            
                    def remove_spaces_from_keys(d):
                        new_dict = {}
                        for key, value in d.items():
                            if isinstance(value, dict):
                                # If the value is a dictionary, recursively call the function
                                new_value = remove_spaces_from_keys(value)
                            else:
                                new_value = value
                            new_dict[key.replace(' ', '_')] = new_value
                        return new_dict

                    def replace_nan_with_none(input_dict):
                        new_dict = {}
                        for key, value in input_dict.items():
                            new_value = {}
                            for k, v in value.items():
                                if isinstance(v, float) and math.isnan(v):
                                    new_value[k] = None
                                else:
                                    new_value[k] = v
                            new_dict[key] = new_value
                        return new_dict
                    data = remove_spaces_from_keys(data)
                    # print(data)
                    modified_data = replace_nan_with_none(data)
                    print("=============================================================================================================================")
                    print(modified_data)
                    print("=============================================================================================================================")


                    message_to_send = json.dumps({"message":modified_data})
                    await websocket.send(message_to_send)



                # message_to_send = "Hello, WebSocket!"
                # await self.send_to_websocket_group(message_to_send)
                # print(f"Sent: {message_to_send}")
                # try:
                #     message_received = await websocket.recv()
                #     print(f"Received:***************************************************************>{message_received}")
                # except asyncio.TimeoutError:
                #     print("No message received in the last 5 seconds.")
                    await asyncio.sleep(1)

                    # sys.exit(1)
                    # c = c+1
                else:
                    print("**************** connection closed ***********************")        
                
               

if __name__ =="__main__":
    # StockDetail()
    # asyncio.run(StockDetail().connect_to_websocket())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(StockDetail().connect_to_websocket())



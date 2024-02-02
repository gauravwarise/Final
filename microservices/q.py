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

baseURL="http://127.0.0.1:1234"
wsURL="ws://127.0.0.1:1234"

class StockDetail(ConnectToAPI):
    def __init__(self):
        super().__init__()

        self.flag = 1
        self._pickleFile = "session.pkl"
        self._sessionData = None

        try:
            with open(self._pickleFile, "rb") as file:
                self._sessionData = pickle.load(file)
        except Exception as e:
            print("while reading pickle", e)

        data = {
            "username": "microservice",
            "password": '12345678',
            "role": "microservice",
            "loginURL": baseURL + "/account/login/",
            "wsURL": wsURL + "/ws/stock/"
        }
        if self._login(data):
            asyncio.run(self.main())
        else:
            print("Login failed. WebSocket connection not established.")

    async def connect_to_websocket(self, websocket):
        try:
            sessionid = self._sessionData.sessionid
            csrf = self._sessionData.csrf
            print(sessionid, csrf)
        except Exception as e:
            print(e)

        headers = {"Cookie": f"csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}"}

        async with websockets.connect(self._wsURL, extra_headers=headers) as websocket:
            try:
                stocklist = await websocket.recv()
                stocklist_dict = json.loads(stocklist)
                stockpicker = stocklist_dict.get('message')
                print(f"Received:***************************************************************>{stockpicker}")
            except asyncio.TimeoutError:
                print("No message received in the last 5 seconds.")

            if stockpicker and len(stockpicker) > 0:
                while self.flag > 0:
                    await self.process_stockpicker(websocket, stockpicker)
                    await asyncio.sleep(1)

    async def process_stockpicker(self, websocket, stockpicker):
        data = {}
        n_threads = len(stockpicker)
        thread_list = []
        que = queue.Queue()

        for i in range(n_threads):
            thread = Thread(target=lambda q, arg1: q.put({stockpicker[i]: get_quote_table(arg1)}),
                            args=(que, stockpicker[i]))
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
        modified_data = replace_nan_with_none(data)
        print("=============================================================================================================================")
        print(modified_data)
        print("=============================================================================================================================")

        message_to_send = json.dumps({"message": modified_data})
        await websocket.send(message_to_send)

    async def receive_stocklist(self, websocket):
        try:
            stocklist = await websocket.recv()
            stocklist_dict = json.loads(stocklist)
            stockpicker = stocklist_dict.get('message')
            print(f"Received:***************************************************************>{stockpicker}")
        except asyncio.TimeoutError:
            print("No message received in the last 5 seconds.")

        if stockpicker and len(stockpicker) > 0:
            while self.flag > 0:
                await self.process_stockpicker(websocket, stockpicker)
                await asyncio.sleep(1)
                # SystemExit(1)
                sys.exit(1)

    async def main(self):
        try:
            sessionid = self._sessionData.sessionid
            csrf = self._sessionData.csrf
            print(sessionid, csrf)
        except Exception as e:
            print(e)

        headers = {"Cookie": f"csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}"}

        async with websockets.connect(self._wsURL, extra_headers=headers) as websocket:
            await asyncio.gather(
                self.connect_to_websocket(websocket),
                self.receive_stocklist(websocket)
            )
    

if __name__ =="__main__":
    StockDetail()
    # stock_detail = StockDetail()
    # asyncio.run(stock_detail.main())
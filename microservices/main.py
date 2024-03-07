from connectToAPI import ConnectToAPI
import pickle
import json
import time
import asyncio
import websockets
from utils import *
import math

from threading import Thread
# import mul
import queue
import websocket

baseURL = "http://127.0.0.1:1234"
wsURL = "ws://127.0.0.1:1234"

class StockDetail(ConnectToAPI):
    def __init__(self):
        super().__init__()

        self.flag = 1
        self._pickleFile = "session.pkl"
        self._sessionData = None
        self.stockpicker = []

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
            self.connect_to_websocket()
        else:
            print("Login failed. WebSocket connection not established.")

    def receive_stock_list(self, websocket):
        print("---------------- receive_stock_list is working ----------------")
        while True:
            try:
                stocklist = websocket.recv()
                stocklist_dict = json.loads(stocklist)

                self.stockpicker = stocklist_dict.get('message')
                print(f"Received:***************************************************************>{self.stockpicker}")
            except websockets.exceptions.ConnectionClosedError:
                print("WebSocket connection closed.")
        
    def process_stock_data(self, websocket):
        
        # if  len(self.stockpicker)>0:
            thread_list = []
            while self.flag > 0:
                print("++++++++++++ process_stock_data is working +++++++++++++++",self.stockpicker)
                data = {}
                n_threads = len(self.stockpicker)
                que = queue.Queue()

                # for i in range(n_threads):
                #     thread = Thread(target=lambda q , arg1: q.put({self.stockpicker[i]: get_quote_table(arg1)}),
                #                     args=(que, self.stockpicker[i]))
                #     thread_list.append(thread)
                #     thread_list[i].start()
                
                for symbol in self.stockpicker:
                    thread = Thread(target=lambda q, sym: q.put({sym: get_quote_table(sym)}),
                                    args=(que, symbol))
                    thread_list.append(thread)
                    thread.start()

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
                print(
                    "=============================================================================================================================")
                print(modified_data)
                print(
                    "=============================================================================================================================")

                message_to_send = json.dumps({"message": modified_data})
                websocket.send(message_to_send)
                time.sleep(1)

    def connect_to_websocket(self):
        try:
            sessionid = self._sessionData.sessionid
            csrf = self._sessionData.csrf
            print(sessionid,     )
        except Exception as e:
            print(e)

        headers = {"Cookie": f"csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}"}
        # with websocket.create_connection(self._wsURL, extra_headers=headers) as websocket:
        self.websocket = websocket.create_connection(self._wsURL,cookie=f"csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}")

        Thread(target=self.receive_stock_list, args=(self.websocket,)).start()
        try:
            Thread(target=self.process_stock_data, args=(self.websocket,)).start()
        except Exception as e:
            print(e)

        # try:
        #     stocklist = self.websocket.recv()
        #     stocklist_dict = json.loads(stocklist)

        #     stockpicker = stocklist_dict.get('message')
        #     print(f"Received:***************************************************************>{stockpicker}")
        # except websockets.exceptions.ConnectionClosedError:
        #     print("WebSocket connection closed.")

        # if len(stockpicker) > 0:
        #     while self.flag > 0:
        #         data = {}
        #         n_threads = len(stockpicker)
        #         thread_list = []
        #         que = queue.Queue()

        #         for i in range(n_threads):
        #             thread = Thread(target=lambda q, arg1: q.put({stockpicker[i]: get_quote_table(arg1)}),
        #                             args=(que, stockpicker[i]))
        #             thread_list.append(thread)
        #             thread_list[i].start()

        #         for thread in thread_list:
        #             thread.join()

        #         while not que.empty():
        #             result = que.get()
        #             data.update(result)

        #         def remove_spaces_from_keys(d):
        #             new_dict = {}
        #             for key, value in d.items():
        #                 if isinstance(value, dict):
        #                     new_value = remove_spaces_from_keys(value)
        #                 else:
        #                     new_value = value
        #                 new_dict[key.replace(' ', '_')] = new_value
        #             return new_dict

        #         def replace_nan_with_none(input_dict):
        #             new_dict = {}
        #             for key, value in input_dict.items():
        #                 new_value = {}
        #                 for k, v in value.items():
        #                     if isinstance(v, float) and math.isnan(v):
        #                         new_value[k] = None
        #                     else:
        #                         new_value[k] = v
        #                 new_dict[key] = new_value
        #             return new_dict

        #         data = remove_spaces_from_keys(data)
        #         modified_data = replace_nan_with_none(data)
        #         print(
        #             "=============================================================================================================================")
        #         print(modified_data)
        #         print(
        #             "=============================================================================================================================")

        #         message_to_send = json.dumps({"message": modified_data})
        #         self.websocket.send(message_to_send)
        #         time.sleep(2)


if __name__ == "__main__":
    StockDetail()

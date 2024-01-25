from connectToAPI import ConnectToAPI
import pickle
import json
import time
import asyncio
import websockets


baseURL="http://127.0.0.1:1234"
wsURL="ws://127.0.0.1:1234"

class StockDetail(ConnectToAPI):
    def __init__(self):
        super().__init__()

        self.flag = 1
        self._pickleFile = "session.pkl"
        self._sessionData = None

        try :
            with open(self._pickleFile,"rb") as file :
                self._sessionData = pickle.load(file)    
        except Exception as e:
            print("while reading pickle",e)

        data = {
            "username": "gaurav",
            "password": '12345678',
            "role":"microservice",
            "loginURL": baseURL+"/account/login/",
            "wsURL": wsURL+"/ws/stock/"
        }
        if self._login(data):
            asyncio.run(self.connect_to_websocket())
        else:
            print("Login failed. WebSocket connection not established.")
     
    async def connect_to_websocket(self):
        headers = {"Cookie": f"csrftoken={self._sessionData.csrf}"}
        async with websockets.connect(self._wsURL,extra_headers=headers) as websocket:
            while self.flag>0:
                message_to_send = json.dumps({"message":f"Hello, WebSocket!"})
                await websocket.send(message_to_send)
                print(f"Sent: {message_to_send}")
                try:
                    message_received = await websocket.recv()
                    print(f"Received: {message_received}")
                except asyncio.TimeoutError:
                    print("No message received in the last 5 seconds.")
                await asyncio.sleep(1)

if __name__ =="__main__":
    StockDetail()
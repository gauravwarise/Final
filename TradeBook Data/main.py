import requests, pickle,json
from connectToApi import ConnectToAPI
import websocket

# baseURL="https://www.cosmicrms.com/api"
# wsURL="wss://www.cosmicrms.com/api"
baseURL="http://192.168.15.63:8500"
wsURL="ws://192.168.15.63:8500"

class Tradesender(ConnectToAPI):
    def __init__(self):
        super().__init__()
        self.flag = 1
        self._pickleFile = "session.pkl"
        self._sessionData = None
        try : 
            with open(self._pickleFile,"rb") as file :
                self._sessionData = pickle.load(file)    
        except Exception as e:
            print("while reading pickle",e, self._sessionData)

        data = {
            "username": "mt5",
            "password": 'Mt5@#1234',
            "loginURL": baseURL+"/account/login",
            "wsURL": wsURL+"/ws/v1/"
        }
        
        if self._sessionData :
            print("====== logout in process")
            self.logout()
        self._login(data)

        self.connectWebSocket()

    def connectWebSocket(self):
        try:
            try:
                with open(self._pickleFile, "rb") as file:
                    self._sessionData = pickle.load(file)
            except Exception as e:
                print("while reading pickle", e)
            print(f"csrftoken={self._sessionData .csrf};sessionid={self._sessionData .sessionid}")
            self.websocket = websocket.create_connection(self._wsURL,cookie=f"csrftoken={self._sessionData .csrf};sessionid={self._sessionData .sessionid}")
        except Exception as e:
            print("Error on connectWebSocket ",e)

    def make_post_request(self, url, data, headers=None):
        try:
            if headers is None:
                headers = {
                    'X-CSRFToken': f'{self._sessionData.csrf}',
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self._sessionData.accesstoken}',
                    'Cookie': f'access_token={self._sessionData.accesstoken}; csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}'
                }
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  
            print(f"POST Request to {url} successful")
            print("Response Status Code:", response.status_code)
          
        except requests.exceptions.RequestException as e:
            print(f"Error making POST request: {e}")


    def recieveWebsocket(self,msg):
        self.websocket.send(msg)
        print(self.websocket.recv())
        while self.flag>0:
            try:
                data = json.loads(self.websocket.recv())
                if data.get('event')=='tradebook' :
                    print(data)
            except :
                pass


endpoint_url = "http://192.168.15.63:8500/dashboard/download"

post_data = {
    "event": "gettradebook",
    "data": {
        "fromdate": "2024-01-02",
        "todate": "2024-01-02",
        "filters": {
            "exchange": ["NSEIFSC"],
            "symbol": ["NIFTY"],
            "userid": ["CNFD07"]
        }
    }
}

obj = Tradesender()
# # obj.make_post_request(endpoint_url, post_data)
# print("=======================",obj._sessionData.accessuserid )

# subscriptionMSG = {
#     "event":"subscribe",
#     "stream":"tradebook",
#     "data":{
#         "userid_id":obj._sessionData.accessuserid 
#     }
# }
# # obj.recieveWebsocket(json.dumps(subscriptionMSG))

# unsubscriptionMSG = {
#     "event":"unsubscribe",
#     "stream":"tradebook",
#     "data":{
#         "userid_id":obj._sessionData.accessuserid 
#     }
# }

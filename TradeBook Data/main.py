import requests, pickle,json
from connectToApi import ConnectToAPI


baseURL="http://www.cosmicrms.com/api"
wsURL="ws://www.cosmicrms.com/api"
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
            print("while reading pickle",e)
        data = {
            "username": "mt5",
            "password": 'Mt5@#1234',
            "loginURL": baseURL+"/account/login",
            "wsURL": wsURL+"/ws/v1/"
        }
        # Run login once
        self.logout()
        self._login(data)

        # AFTER LOGIN TO RECIEVE TRADEBOOOK FROM SOCKET
        self.connectWebSocket()

    def make_post_request(self, url, data, headers=None):
        try:
            
            # Initialize headers if not provided
            if headers is None:
                headers = {
                    'X-CSRFToken': f'{self._sessionData.csrf}',
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self._sessionData.accesstoken}',
                    'Cookie': f'access_token={self._sessionData.accesstoken}; csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}'
                }

            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

            # If the response contains JSON data, you can access it like this:
            json_data = response.json()

            # Print the response details
            print(f"POST Request to {url} successful")
            print("Response Status Code:", response.status_code)
            print("Response JSON:", json_data)

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


# Specify the endpoint URL
endpoint_url = "http://192.168.15.63:8500/dashboard/download"



# Specify the data you want to send in the POST request
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
# obj.make_post_request(endpoint_url, post_data)

subscriptionMSG = {
    "event":"subscribe",
    "stream":"tradebook",
    "data":{
        "userid_id":obj._sessionData.accessuserid 
    }
}
print(subscriptionMSG)
obj.recieveWebsocket(json.dumps(subscriptionMSG))

unsubscriptionMSG = {
    "event":"unsubscribe",
    "stream":"tradebook",
    "data":{
        "userid_id":obj._sessionData.accessuserid 
    }
}

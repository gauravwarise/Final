import pickle,os,requests
from json import loads
import sys,time
import websocket

baseURL="http://127.0.0.1:1234"
wsURL="ws://127.0.0.1:1234"

class ConnectToAPI :

    """
        Class : ConnectToAPI 
        params to pass in constructor : 
            username : username provided for loggin in to rest api of rms
    
    """

    def __init__(self) :
        self._pickleFile = "session.pkl"
        self._sessionData = None
        try :
            with open(self._pickleFile,"rb") as file :
                self._sessionData  = pickle.load(file)    
        except Exception as e:
            print(e)

    def dataSerializer(self,__data):
        """
            CHECKING FOR KEYS IN DATA 
        """
        if isinstance(__data,dict):
            try:
                self.__username = __data["username"]
                self.__password = __data["password"]
                self.role = __data["role"]
                self.__loginURL = __data["loginURL"]
                self._wsURL = __data["wsURL"]
            except KeyError as e:
                raise KeyError(str(e)+ "is missing please check")                  
        else :
            raise TypeError("Object of unsupproted type cannot be serialized")
    
    
    def _login(self,creds=dict()):
        self.dataSerializer(creds)           

        try:
            __body = {
                
                    "username":self.__username,
                    "password":self.__password,
                    "role":self.role
            }
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            __response = requests.post(url=self.__loginURL,data=__body, headers=headers)
            if __response.status_code == 200 : 
                print("============== login successfully ================") 
                try:
                    __session = Session(csrf=__response.cookies.get("csrftoken"))
                    with open(self._pickleFile,"wb") as f :
                        pickle.dump(__session,f)   
                    response_data = loads(__response.text)
                except Exception as e:
                    print(e)
                return response_data
            else:
                print("============== login Failed ================") 
                response_data = loads(__response.text)
                return response_data
        except Exception as e:
            return None
    
    def logout(self):
        try:
            logout_url = baseURL + "/account/logout"
            headers = {
                'X-CSRFToken': f'{self._sessionData.csrf}',
                'Cookie': f'csrftoken={self._sessionData.csrf};'
            }
            response = requests.post(url=logout_url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
   
    def connectWebSocket(self):
        try:
            self.websocket = websocket.create_connection(self._wsURL,cookie=f"csrftoken={self._sessionData .csrf};")
        except Exception as e:
            print(e)
    
    def disconnectwebsocket(self):
        if self.websocket:
            self.websocket.close()

class Session :
    """
        setter and getter class to store data in pickle file
    """

    def __init__(self,**kwargs) :
        self.__csrf = kwargs.get("csrf",None)



    @property
    def csrf(self):
        return self.__csrf     

    @csrf.setter
    def csrf(self,value):
        self.__csrf = value

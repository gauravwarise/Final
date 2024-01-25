import pickle,os,requests
from json import loads
import sys,websocket,time

baseURL="http://www.cosmicrms.com/api"
wsURL="ws://www.cosmicrms.com/api"

class ConnectToAPI :

    """
        Class : ConnectToAPI 
        params to pass in constructor : 
            username : username provided for loggin in to rest api of rms
    
    """

    def __init__(self) :
        pass
        self._pickleFile = "session.pkl"
        self._sessionData = None
        try :
            with open(self._pickleFile,"rb") as file :
                self._sessionData  = pickle.load(file)    
        except Exception as e:
            print("while reading pickle",e)
        

    def dataSerializer(self,__data):
        """
            CHECKING FOR KEYS IN DATA 
        """
        if isinstance(__data,dict):
            try:
                self.__username = __data["username"]
                self.__password = __data["password"]
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
                "event":"login",
                "source":"web",
                "data":{
                    "username":self.__username,
                    "password":self.__password
                }
            }
            __response = requests.post(url=self.__loginURL,json=__body)
            if __response.status_code == 200 :                
                __session = Session(sessionid=__response.cookies.get("sessionid"),csrf=__response.cookies.get("csrftoken"),accesstoken=loads(__response.text).get("access_token"),
                                    accessuserid =loads(__response.text).get("accessusers") )
                print(loads(__response.text).get("accessusers"))
                with open(self._pickleFile,"wb") as f :
                    pickle.dump(__session,f)   
                # print("logged in successfully")
                response_data = loads(__response.text)
                
                return response_data
            else:
                # print("Response from API==========================:", __response.text)
                response_data = loads(__response.text)
                # already_logged_in = response_data.get("isalreadyloggedin")                
                return response_data
        except Exception as e:
            return None


    def delete_session(self,data):
        try:
            # Specify the endpoint URL for session deletion
            delete_session_url = baseURL+ "/account/deletesession"
            # delete_session_url = "http://192.168.15.63:8500/account/deletesession"

            # Initialize headers
            headers = {
                'X-CSRFToken': f'{self._sessionData.csrf}',
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self._sessionData.accesstoken}',
                'Cookie': f'access_token={self._sessionData.accesstoken}; csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}'
            }
            print("******************headers from delete session*********************", headers)

            # Make a POST request to delete the session
            response = requests.post(url=delete_session_url, json=data, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

            # Print the response details
            print(f"DELETE Session Request {delete_session_url} successful")
            print("Response Status Code from delete session:", response.status_code)
            print("Response JSON from delete session:", response.json())

        except requests.exceptions.RequestException as e:
            print(f"Error making DELETE session request: {e}")

    def logout(self):
        try:
            # Specify the endpoint URL for User Logout
            # logout_url = "http://192.168.15.63:8500/account/logout"
            logout_url = baseURL + "/account/logout"

            # Initialize headers
            headers = {
                'X-CSRFToken': f'{self._sessionData.csrf}',
                'Authorization': f'Bearer {self._sessionData.accesstoken}',
                'Cookie': f'access_token={self._sessionData.accesstoken}; csrftoken={self._sessionData.csrf}; sessionid={self._sessionData.sessionid}'
            }

            # Make a GET request to logout
            response = requests.get(url=logout_url, headers=headers)
            response.raise_for_status()  # Check for HTTP errors

            # Print the response details
            print(f"GET logout Request to {logout_url} successful")
            print("Response Status Code from logout:", response.status_code)
            print("Response JSON from logout:", response.json())

        except requests.exceptions.RequestException as e:
            print(f"Error making GET logout request: {e}")



    def connectWebSocket(self):
        try:
            self.websocket = websocket.create_connection(self._wsURL,cookie=f"csrftoken={self._sessionData .csrf};sessionid={self._sessionData .sessionid}")
        except Exception as e:
            print("Error on connectWebSocket ",e)


class Session :
    """
        setter and getter class to store data in pickle file
    """

    def __init__(self,**kwargs) :
        self.__sessionid = kwargs.get("sessionid",None)
        self.__csrf = kwargs.get("csrf",None)
        self.__accesstoken = kwargs.get("accesstoken",None)
        self.__accessuserid = kwargs.get("accessuserid",None)

    @property
    def sessionid(self):
        return self.__sessionid     

    @sessionid.setter
    def sessionid(self,value):
        self.__sessionid = value

    @property
    def csrf(self):
        return self.__csrf     

    @csrf.setter
    def csrf(self,value):
        self.__csrf = value

    @property
    def accesstoken(self):
        return self.__accesstoken
    
    @accesstoken.setter
    def accesstoken(self,value):
        self.__accesstoken = value 

    @property
    def accessuserid(self):
        return self.__accessuserid
    
    @accessuserid.setter
    def accessuserid(self,value):
        self.__accessuserid = value 
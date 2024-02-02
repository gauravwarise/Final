from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
# from django.contrib.auth.models import User
from apps.core.models import *

from django.contrib import auth
from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
# Create your views here.

from django.contrib.auth.hashers import check_password
from django.views.decorators.cache import never_cache

from apps.core.utils import is_user_logged_in
from django.contrib.auth.models import AnonymousUser
# from user_sessions.models import Session

from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model

from apps.core.serializers import AuthUserSerializer
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from django.http import JsonResponse
from rest_framework_simplejwt.tokens import RefreshToken



from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt


from yahoo_fin.stock_info import *



from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from channels.db import database_sync_to_async





class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse(
                {
                    'username_error':'username should only contain alphanumeric characters',
                    },
                    status=400)
        if AuthUser.objects.filter(username=username).exists():
            return JsonResponse(
                {
                    'username_error':'sorry username in use, choose another one ',
                    },
                    status=409)
        return JsonResponse({'username_valid':True})

class RegistrationView(View):
    def get(self, request):
        return render(request, 'account/register.html') 
    
    def post(self, request):
        # GET USER DATA
        # VALIDATE
        # create a user account
        print("request has be got ====================")
        print(request.POST)
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST.getlist('role')
        print("===========>", username, email, role)

        
        # password = make_password(password)
        print(password)

        context = {
            'fieldValues': request.POST
        }

        # messages.success(request, 'success whatsapp')
        print("username===================", username)

        if not AuthUser.objects.filter(username=username).exists():
            if not AuthUser.objects.filter(email=email).exists():
                print("insite condition===")
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'account/register.html', context)

                # user = AuthUser.objects.create(username=username, email=email, password = password)
                # # user.set_password(password)
                # user.set_password(password)
                # user.is_active = True
                # user.save()

                user = get_user_model().objects.create_user(
                    username=username, email=email, password=password, role=role[0]
                )
                user.is_active = True
                user.save()


                # current_site = get_current_site(request)
                # email_body = {
                #     'user': user,
                #     'domain': current_site.domain,
                #     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                #     'token': account_activation_token.make_token(user),
                # }

                # link = reverse('activate', kwargs={
                #                'uidb64': email_body['uid'], 'token': email_body['token']})

                # email_subject = 'Activate your account'

                # activate_url = 'http://'+current_site.domain+link

                # email = EmailMessage(
                #     email_subject,
                #     'Hi '+user.username + ', Please the link below to activate your account \n'+activate_url,
                #     'noreply@semycolon.com',
                #     [email],
                # )
                # email.send(fail_silently=False)
                messages.success(request, 'Account successfully created')
                print('Account successfully created==============')
                return render(request, 'account/login.html')
            else:
                messages.error(request, 'email is already in use')
                return render(request, 'account/register.html', context)
        return render(request, 'account/register.html')

    # def post(self, request):
    #     # ... (your existing code)
    #     # username = request.POST['username']
    #     # email = request.POST['email']
    #     # password = request.POST['password']

    #     # if not get_user_model().objects.filter(username=username).exists():
    #     #     if not get_user_model().objects.filter(email=email).exists():
    #     #         if len(password) < 6:
    #     #             messages.error(request, 'Password too short')
    #     #             return render(request, 'account/register.html', context)

    #     #         # Use create_user to automatically hash the password
    #     #         print("-------------------")
    #     #         user = get_user_model().objects.create_user(
    #     #             username=username, email=email, password=password
    #     #         )
    #     #         user.is_active = True
    #     #         user.save()
    #     #         print("saved")

    #     #         messages.success(request, 'Account successfully created')
    #     #         return render(request, 'account/login.html')
    #     #     else:
    #     #         messages.error(request, 'Email is already in use')
    #     #         return render(request, 'account/register.html', context)

    #     # serializer = AuthUserSerializer(data=request.POST)
    #     # if serializer.is_valid():
    #     #     serializer.save()
    #     #     print("user has been saved ")
    #     #     return render(request, 'account/login.html')
    #     # print("serializer is not va;id")
    #     # # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     # return render(request, 'account/register.html')



@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(ensure_csrf_cookie, name='dispatch')
class LoginView(View):
    def get(self, request):
        return render(request, 'account/login.html')
    
    def post(self, request):
        print("//////////////////")

        response = {"status": "success", "errorcode": "","reason": "", "result": "", "httpstatus": 200}

        # __data = json.loads(request.body.decode('utf-8'))  
        # __username = str(__data['username'])
        # __password = __data['password'] 
        __username = request.POST.get('username')
        __password = request.POST.get('password')
        role = request.POST.get('role', None)
        print(__username, __password, role)
        # role = "microservices"
        exist_user = AuthUser.objects.get(username=__username)
        print(exist_user.role)
        if role:
            if role=="microservice":
                print("================= inside if ======")
                # __data = json.loads(request.body.decode('utf-8'))  
                # __username = str(__data['username'])
                # __password = __data['password'] 
                print(__username, __password)
                response = {"status": "success", "errorcode": "","reason": "", "result": "", "httpstatus": 200}
                user = authenticate(request=request, username=__username, password=__password)
                print("user ===================<<<<<<<<<<<<<<", user.id)
                login(request, user)
                request.session['username'] = __username
                request.session['user_id'] = user.id
                request.session['role'] = role


                channel_layer = get_channel_layer()
                stockpicket_group_name = "stockpicker_group"
                async_to_sync(channel_layer.group_add)(stockpicket_group_name,f"user_{user.id}")
                print('chanel layer: ====',channel_layer)
                is_user_in_group = self.is_user_in_channel_group(stockpicket_group_name, f"user_{user.id}")
                if is_user_in_group:
                    print(f"microservice {__username} successfully added to group {stockpicket_group_name}")
                else:
                    print(f"Failed to add user {__username} to group {stockpicket_group_name}")



            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            sessionid = request.session.session_key
            response['sessionid'] = sessionid
            print("???????????????", sessionid)

            response['access_token'] = access_token
            response['status'] = "success"
            response['role'] = role
            resp = JsonResponse(response, status=response.get(
                'httpstatus', 200))
            resp.set_cookie('access_token', access_token)
            resp.set_cookie('sessionid', sessionid)
            return resp 
        # username = request.POST['username']
        # password = request.POST['password']

        # print("====>",request.user.is_authenticated)
        
        

        # if role == "microservices":
        #     user = authenticate(request=request,username=username, password=password)

        #     refresh = RefreshToken.for_user(user)
        #     access_token = str(refresh.access_token)
        #     print(access_token)
        #     resp = JsonResponse(response, status=response.get(
        #                         'httpstatus', 200))
        #     resp.set_cookie('access_token', access_token)
        #     return resp

        # print(username,password)

        # user = authenticate(request=request,username=username, password=password)
        # print(user.password)


        # # The stored hashed password
        # stored_password = "pbkdf2_sha256$600000$OaAsdFeG5As91TxU9QPMmI$arCnv5pftsyKIoa4HPs2zLfyZEO6ZH14i7c8oMVaJRs="

        # # The user's entered password
        # user_password = password

        # # Check if the user's entered password matches the stored hashed password
        # if check_password(user_password, stored_password):
        #     print("===========Password is correct.")
        # else:
        #     print("=============Password is incorrect.")

        # if User.objects.filter(username=username).exists():
        #     print("========== valid username")

        # if User.objects.filter(password=password).exists():
        #     print("========== valid password")
        # # user = User.objects.get(username=username and password=password)
        # user = User.objects.get(username=username)

        # print("userpassword is .....................",user.password)
        
        user = request.user
        print("========== || check session || ==========", user,request.session)

        if __username and __password:
            user = authenticate(request=request, username=__username, password=__password)
            # print(user)
            # print(user.id)
            active_sessions = Session.objects.filter(
                    expire_date__gte=timezone.now(),
                    # user=user
                )
            # .exclude(session_key=request.session.session_key)
            # if active_sessions.:
            #        print("user is already logged in")
            for session in active_sessions:
                session_data = session.get_decoded()
                # print(session_data, session_data.get('_auth_user_id'))
                auth_user_id = session_data.get('_auth_user_id')
                if auth_user_id is not None and user.id == int(auth_user_id):
                    # print("\\\\\\\\\\\\\\\\\\\\\\\\user is exist")
                    user_exists = True
                    return render(request, 'account/login.html', {'user_exists': user_exists, 'username':__username, 'password':__password})
                else:
                    pass

            # print(is_user_logged_in(user), active_sessions)
            

            if user is not None:
                # print("============================")
                # print("========", user.id)
                if user.is_active:
                    login(request, user)
                    request.session['username'] = __username
                    print("user ========================>", user.id, user.role)
                    request.session['id'] = user.id
                    request.session['role'] = user.role
                    # user = request.user
                    # role = user.role
                    # request.session['role'] = role

                    # channel_layer = get_channel_layer()
                    # room_group_name = "testw_consumer_group"
                    # async_to_sync(channel_layer.group_add)(room_group_name, f"user_{user.id}")
                    # print('chanel layer: ====',channel_layer)
                    # is_user_in_group = self.is_user_in_channel_group(room_group_name, f"user_{user.id}")
                    # if is_user_in_group:
                    #     print(f"User {user.username} successfully added to group {room_group_name}")
                    # else:
                    #     print(f"Failed to add user {user.username} to group {room_group_name}")


                    # messages.success(request, 'Welcome, ' +
                    #                  user.username+' you are now logged in')
                    
                    # available_stocks = tickers_nifty50()
                    # print(available_stocks)
                    
                    # return render(request, 'dashboard/dashboard.html', {'stockpicker': available_stocks, 'user': user, 'role': role})
                    # return render(request,'dashboard/dashboard.html', {'stockpicker': available_stocks,'user': user, 'role': role})
                    return redirect('dashboard')


                messages.error(
                    request, 'Account is not active,please check your email')
                return render(request, 'account/login.html')
            messages.error(
                request, 'Invalid credentials,try again')
            return render(request, 'account/login.html')

        messages.error(
            request, 'Please fill all fields')
        return render(request, 'account/login.html')

    @database_sync_to_async
    def is_user_in_channel_group(room_group_name, channel_name):
        channel_layer = get_channel_layer()
        group_channels = async_to_sync(channel_layer.group_channels)(room_group_name)
        return channel_name in group_channels
    # def post(self, request):
    #     username = request.POST["username"]
    #     password = request.POST["password"]
    #     print("=============== ", username, password)

    #     if username and password:
    #         user = auth.authenticate(username = username, password=password)
    #         print(user)
    #         if user:
    #             if user.is_active:
    #                 auth.login(request, user)
    #                 messages.success(request, "Welcome, " + user.username + " you are now logged in...")
    #             messages.error(request, "Account is not active, please check your email...")
    #             return render(request, 'account/login.html')
    #         messages.error(request, "Invalid credentials, try again...")
    #         return render(request, 'account/login.html')


class LogoutView(View):
    def post(self, request):
        print("before logut")
        print("==========================session data after logout",request.session['username'])
        logout(request)
        active_sessions = Session.objects.filter(
                    expire_date__gte=timezone.now(),
                    # user=user
                )
            # .exclude(session_key=request.session.session_key)
            # if active_sessions.:
            #        print("user is already logged in")
        for session in active_sessions:
            session_data = session.get_decoded()
            print(session_data, session_data.get('_auth_user_id'))

        print( active_sessions)
        messages.success(request, "You have been lagged out")
        request.session.flush() 
        # print("==========================session data after logout",request.session['username'])
        if not request.session:
            print("Session is empty.")
        else:
            print("Session is not empty.")
        
        


        return redirect('login')



class CheckSession(View):
    def get(self, request):
        try:
            user = request.user
            print("========== || check session || ==========", user,request.session)
        except Exception as e:
            print(e)

class DeleteSession(View):
    def post(self, request):


        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        print(username, password, user, user.id)




        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now())

        for session in active_sessions:
            session_data = session.get_decoded()
            print("========>",request.user.id, session_data.get('_auth_user_id'))
            auth_user_id = session_data.get('_auth_user_id')
            if auth_user_id is not None and user.id == int(auth_user_id):
                session.delete()
                return redirect('login')
        
        return JsonResponse({'message': 'Session deleted successfully'})
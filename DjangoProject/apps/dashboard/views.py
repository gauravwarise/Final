from django.shortcuts import render
from rest_framework.views import APIView
from yahoo_fin.stock_info import *
from django.http import HttpResponse
from threading import Thread
import queue
import pandas as pd
from io import StringIO
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .utils import get_quote_table


# @login_required
@method_decorator(login_required, 'dispatch')
class DashboardView(APIView):
    def get(self, request):
        stock_tickers = tickers_nifty50()
        username = request.session.get('username') 
        print("======>",username)
        
        return render(request, 'dashboard/dashboard.html', {'stockpicker': stock_tickers, 'username':username})




class HomeView(APIView):
    def get(self, request):
        return render(request, 'dashboard/home.html')



# @login_required
@method_decorator(login_required, 'dispatch')
class StockTracker(APIView):

    def my_get_quote_table(self, symbol):
        # site = f'https://finance.yahoo.com/quote/{symbol}?p={symbol}&.tsrc=fin-srch'

        site = f'https://finance.yahoo.com/quote/{symbol}?p={symbol}&.tsrc=fin-srch'

        # Define headers to simulate a user agent (optional but recommended)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        # Make the HTTP request and read HTML tables
        html_content  = requests.get(site, headers=headers).text

        # Wrap HTML content in StringIO
        html_stringio = StringIO(html_content)

        # Read HTML tables from StringIO
        tables = pd.read_html(html_stringio)

        # Concatenate the DataFrames in tables list
        data = pd.concat(tables, axis=0)

        return data


    def get(self, request):
        print("stocktracker view called==============================")

        # Get stockpicker from request.GET
        stockpicker = request.GET.getlist('stockpicker')
        # stock_tickers = tickers_nifty50()

        print(stockpicker)

        data = {}
        available_stocks = tickers_nifty50()

        for i in stockpicker:
            if i in available_stocks:
                pass
            else:
                return HttpResponse("Error")

        # for i in stockpicker:
        #     print(i)
        #     details = self.my_get_quote_table(i)
        #     data.update({i:details.to_dict()})
            
        # print(data)

        # Your code to process the details goes here

        # return HttpResponse("Success") 
        n_threads = len(stockpicker)
        thread_list = []
        que = queue.Queue()
        
        for i in range(n_threads):
            thread = Thread(target=lambda q, arg1: q.put({stockpicker[i]: get_quote_table(arg1)}), args=(que, stockpicker[i]))
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
        data = remove_spaces_from_keys(data)
        print(data)


        return render(request, 'dashboard/dashboard.html', {'stockpicker': available_stocks, 'data':data})
from celery import shared_task

from yahoo_fin.stock_info import *
from django.http import HttpResponse
from threading import Thread
import queue
import pandas as pd
from io import StringIO
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .utils import get_quote_table


@shared_task(bind=True)
def update_stock(self, stockpicker):
    data = {}
    available_stocks = tickers_nifty50()

    for i in stockpicker:
        if i in available_stocks:
            pass
        else:
            stockpicker.remove(i)

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
    
    return 'Done!!'
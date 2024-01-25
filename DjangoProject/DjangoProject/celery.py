from __future__ import absolute_import, unicode_literals
import os
# from celery import crontab # to schedule task 
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

app = Celery('DjangoProject')
app.conf.enable_utc = False
app.conf.update(timezone = 'Asia/Kolkata')

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_scheduler = {
    'every-10-seconds' : {
        'task':'dashboard.tasks.update_stock',
        'schedule':10,
        'args':(['RELIENCE.NS','BAJAJFINSV.NS'])
    }
}


app.autodiscover_tasks()


# @app.task(bind=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')
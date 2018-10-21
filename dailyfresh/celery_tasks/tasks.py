from celery import Celery
from django.core.mail import send_mail
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dailyfresh.settings")
django.setup()
app = Celery('celery_tasks.tasks',broker='redis://192.168.12.230:6379/3')
# celery -A celery_tasks.tasks worker -l info

@app.task
def task_send_mail(subject,message,sender,receiver,html_message):
    print('开始发......')
    import time
    time.sleep(10)
    send_mail(subject,message,sender,receiver,html_message=html_message)
    print('发完了......')
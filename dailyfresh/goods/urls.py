from django.conf.urls import url
from goods import views
urlpatterns=[
    url(r'^index$', views.TextIndex.as_view(), name='index'),  # 临时首页
]
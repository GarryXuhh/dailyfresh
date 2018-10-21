from django.conf.urls import url
from user import views
from django.contrib.auth.decorators import login_required
urlpatterns=[
    url(r'^register$',views.RegisterView.as_view(),name='register'),#用户注册
    url(r'^vali$',views.vali,name='vali'),#验证码
    url(r'^login$',views.LoginView.as_view(),name='login'),#登录
    url(r'^active/(?P<token>.*)$',views.ActiveView.as_view(),name='active'),#激活
    url(r'^logout$',views.LogoutView.as_view(),name='logout'),
    url(r'^$',views.UserInfoView.as_view(),name='user'),#用户中心-信息页
    url(r'^order$',views.UserOrderView.as_view(),name='order'),#用户中心-订单页
    url(r'^address$',views.UserAddressView.as_view(),name='address'),#用户中心-地址页
    url(r'^resetPWD$',views.ResetPWDView.as_view(),name='resetPWD'),#忘记密码
    url(r'^newPWD/(?P<token>.*)$',views.NewPWDView.as_view(),name='newpwd'),#激活新密码
    url(r'^test_ajax$',views.test_ajax),
    url(r'^test666$',views.test666),
    url(r'^testaddress$',views.testaddress),
]
import re
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic import View
from user.models import *
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer,SignatureExpired,BadSignature
from django.core.mail import  send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from celery_tasks.tasks import task_send_mail
from utils.user_util import *

# Create your views here.
class RegisterView(View):
    '''视图类'''
    def get(self,request):
        # 注册页面
        return render(request, 'register.html')
    def post(self,request):
        # 注册处理
        # 接受数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        cpwd = request.POST.get('cpwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, cpwd, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        if password != cpwd:
            # 密码不一致
            return render(request, 'register.html', {'errmsg': '密码不一致'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})
        vali = request.POST.get('vali','').strip().lower()
        if vali != request.session.get('vali').lower():
            return redirect(reverse('user:register'))
        # 进行业务处理:进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()
        '''
        发送激活邮件
        '''
        #加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info).decode()
        encryption_url='http://192.168.12.230:8888/user/active/%s'%token
        # encryption_url='http://192.168.12.230:8888/user/active/%s'%token

        #发邮件
        subject = '澳门皇冠赌场欢迎您'#主题
        message = '' #文本内容
        sender = settings.EMAIL_FROM #发件人
        receiver = [email]#收件人
        html_message = '<h1>%s,欢迎您成为澳门皇冠赌场注册会员</h1>性感荷官送您80万元人民币试玩筹码，请点击下面的链接以领取<br/><a href="%s">%s</a>'%(username,encryption_url,encryption_url)
        task_send_mail.delay(subject,message,sender,receiver,html_message)
        # send_mail(subject,message,sender,receiver,html_message=html_message)#发送


        # 返回应答，跳转到首页
        return redirect(reverse('user:login'))

class LoginView(View):
    def get(self,request):
        rember = request.COOKIES.get('rember','')
        return render(request,'login.html',{'rember':rember})
    def post(self,request):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        user = authenticate(username=username,password=pwd)
        rember = request.POST.get('rember')
        if user and user.is_active:
            login(request,user)
            next_url = request.GET.get('next')
            if next_url:
                resp = redirect(next_url)
            else:
                resp = redirect(reverse('goods:index'))

            if rember:
                resp.set_cookie('rember',username,3600*24*7)
            else:
                resp.set_cookie('rember',username,0)
            return resp

        else:
            return redirect(reverse('user:login'))

class ActiveView(View):
    def get(self,request,token):
        '''用户激活'''
        #进行解密，获取要激活的信息
        serializer = Serializer(settings.SECRET_KEY,3600)
        try:
            info = serializer.loads(token)
            #获取待激活用户的ID
            user_id = info['confirm']
            #根据ID获取用户信息
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            #跳转到登录页面
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            #激活连接已过期
            return HttpResponse('激活连接已过期')
        except BadSignature as e:
            #激活链接错误
            return HttpResponse('激活链接非法')

def vali(request):
    # 定义变量，用于画面的背景色、宽、高
    bgcolor = (random.randrange(20, 100), random.randrange(
        20, 100), 255)
    width = 120
    height = 40
    # 创建画面对象
    im = Image.new('RGB', (width, height), bgcolor)
    # 创建画笔对象
    draw = ImageDraw.Draw(im)
    # 调用画笔的point()函数绘制噪点
    for i in range(0, 100):
        xy = (random.randrange(0, width), random.randrange(0, height))
        fill = (random.randrange(0, 255), 255, random.randrange(0, 255))
        draw.point(xy, fill=fill)
    # 定义验证码的备选值
    str1 = 'ABCD123EFGHIJK456LMNOPQRS789TUVWXYZ0'
    # 随机选取4个值作为验证码
    rand_str = ''
    for i in range(0, 4):
        rand_str += str1[random.randrange(0, len(str1))]
    # 构造字体对象
    font = ImageFont.truetype('FreeMono.ttf', 30)
    # 构造字体颜色
    fontcolor = (255, random.randrange(0, 255), random.randrange(0, 255))
    # 绘制4个字
    draw.text((14, 8), rand_str[0], font=font, fill=fontcolor)
    draw.text((34, 8), rand_str[1], font=font, fill=fontcolor)
    draw.text((55, 8), rand_str[2], font=font, fill=fontcolor)
    draw.text((80, 8), rand_str[3], font=font, fill=fontcolor)
    # 释放画笔
    del draw
    # 存入session，用于做进一步验证
    request.session['vali'] = rand_str
    # 内存文件操作
    buf = BytesIO()
    # 将图片保存在内存中，文件类型为png
    im.save(buf, 'png')
    # 将内存中的图片数据返回给客户端，MIME类型为图片png
    return HttpResponse(buf.getvalue(), 'image/png')


class UserInfoView(LoginRequiredMixin,View):
    '''用户中心信息页'''
    def get(self,request):
        #获取登录用户对应的User对象
        user = request.user
        #获取用户的默认收获地址
        try:
            address = Address.objects.get(user=user,is_default=True)
        except Address.DoesNotExist:
            #不存在默认收获地址
            address = None

        context = {'page': '1','address': address}
        return render(request,'user_center_info.html',context)

class UserOrderView(LoginRequiredMixin,View):
    '''用户中心信息页'''
    def get(self,request):
        context = {'page':'2'}
        return render(request,'user_center_order.html',context)

class UserAddressView(LoginRequiredMixin,View):
    '''用户中心信息页'''
    def get(self,request):
        #获取登录用户对应的user对象
        user = request.user
        #获取用户的默认收获地址
        try:
            address = Address.objects.get(user=user,is_default=True)
        except Address.DoesNotExist:
            #不存在默认地址
            address = None
        #数据字典
        context = {
            'page':'3',
            'address':address
        }

        return render(request,'user_center_site.html',context)
    def post(self, request):
        '''地址的添加'''
        #接受数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')
        print(receiver)
        print(addr)
        print(zip_code)
        print(phone)
        #校验数据
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})

        #校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
            return render(request, 'user_center_site.html',{'errmsg':'手机号格式不正确'})

        #业务处理：地址添加
        #用户新添加的地址作为默认收获地址，如果原来有收获地址，要取消
        #获取用户的默认收获地址

        #获取登录对象对应User对象
        user = request.user
        try:
            address = Address.objects.get(user=user,is_default=True)
            address.is_default=False
            address.save()
        except Address.DoesNotExist:
            #不存在默认收获地址
            pass
        #添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=True)
        #返回应答，刷新地址页面
        return redirect(reverse('user:address')) #get请求方式

class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect(reverse('goods:index'))

class ResetPWDView(View):
    def get (self,request):
        return render(request,'resetPWD.html')
    def post(self,request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        newpwd = request.POST.get('newpwd')
        user = User.objects.get(username = username)
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'userid':user.id,
                'newpwd':newpwd}
        token = serializer.dumps(info).decode()
        encryption_url = 'http://192.168.12.230:8888/user/newPWD/%s'%token

        #发邮件
        subject = '澳门皇冠赌用户密码找回'#主题
        message = ''
        sender = settings.EMAIL_FROM#发件人
        receiver = [email]#收件人
        html_message = '<h1>欢迎尊贵的澳门皇冠赌场至尊会员，%s</h1>请点击下面的链接确认修改您的密码：<a href="%s">%s</a>'%(username,encryption_url,encryption_url)
        task_send_mail.delay(subject,message,sender,receiver,html_message)

        return redirect(reverse('user:login'))
class NewPWDView(View):
    def get(self,request,token):
        '''新密码激活'''

        serializer = Serializer(settings.SECRET_KEY,3600)
        try:
            info = serializer.loads(token)
            user_id = info['userid']
            newpwd = info['newpwd']
            user = User.objects.get(id=user_id)
            user.set_password(newpwd)
            user.save()

            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            # 激活连接已过期
            return HttpResponse('激活连接已过期')
        except BadSignature as e:
            # 激活链接错误
            return HttpResponse('激活链接非法')
def test_ajax(request):
    return render(request,'test_ajax.html')
def test666(request):
    word = request.GET.get('name')
    return HttpResponse(word)
def testaddress(request):
    return render(request,'testaddress.html')



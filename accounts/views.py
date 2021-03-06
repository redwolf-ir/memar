from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as django_logout
from django.contrib.auth import login as auth_login
from .models import Profile, Passwordresetcodes
from .token import registration_token, password_reset_token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.contrib import messages
from datetime import datetime
import hashlib
import pytz
#------------------------------------------------------------------------------#
def register_view(request):
	# karbar dokme sabt nam ra click karde ast
	if 'requestcode' in request.POST:
		if User.objects.filter(email=request.POST['email']).exists():
			messages.error(request, 'قبلا کاربری با این ایمیل ثبت نام \
			کرده است. اگر اون شخص شمایید از قسمت %s رمز ورود خود را \
			بازیابی کنید.' % '<a href="{% url \'password_reset\' %}">بازیابی پسورد</a>')
			return redirect('register')
        # age karbar to database mojod nabashad
		if not User.objects.filter(username=request.POST['username']).exists():
			email = request.POST['email']
			username = request.POST['username']
			password = request.POST['password']
			password2 = request.POST['password2']
			if password == password2:
				password = make_password(request.POST['password'])
				password2 = None
				user = User(
	            email=email, username=username, password=password)
				user.is_active = False
				user.save()
				token = registration_token(username, email)
				userid = User.objects.get(email=request.POST['email']).id
				send_mail(
					'ثبت نام در معمار دات کام',
					'<a href=\"{}?token={}&id={}\">\
					لینک رو به رو</a>'.format(request.build_absolute_uri\
					('/register/'), token, userid),
					'info@memar.com',
					['{}'.format(email)],
					fail_silently=False,
				)
				messages.success(request, '<a href=\"{}?token={}&id={}\">\
				لینک رو به رو</a>'.format(request.build_absolute_uri\
				('/register/'), token, userid))
				return redirect('register')
			else:
				messages.success(request, "پسوردهای وارد شده با هم برابر نیست.")
		else:
			messages.error(request, "یوزرنیم وارد شده تکراری می باشد. \
			لطفا یکی دیگه انتخاب کنید.")
			return redirect('register')

	# karbar email ersal shode ra click karde ast
	elif 'token' in request.GET and 'id' in request.GET:
		code = request.GET['token']
		userid = request.GET['id']
		thisuser = get_object_or_404(User, id=userid)
		token = registration_token(thisuser.username, thisuser.email)
		if code == token and thisuser.is_active == False:
			now = datetime.now()
			utc = pytz.UTC
			dt = now.replace(tzinfo=utc) - thisuser.date_joined.replace(tzinfo=utc)
			dt= dt.days
			if dt < 1:
				thisuser.is_active = True
				thisuser.save()
				messages.success(request, 'ثبت نام شما با موفقیت انجام شد.')
				Profile.objects.get_or_create(user=request.user)
				return redirect('login')
			else:
				thisuser.delete()
				messages.error(request, 'زمانه استفاده از توکن گذشته است. لطفا\
				مجددا درخواست نمایید.')
				return redirect('register')

		elif code == token and thisuser.is_active == True:
			messages.warning(request, 'از این توکن قبلا استفاده شده است!\
			اگر پسورد خود را گم کرده اید از قسمت %s استفاده کنید.\
			' % '<a href="{% url \'password_reset\' %}">بازیابی پسورد</a>')
		else:
			messages.error(request, 'متاسفانه مشکلی پیش آمده است. لطفا \
			دوباره امتحان کنید.')
		auth_login(request, thisuser)
		return redirect('register')

	# karbar avalin bar ast be safhe register amade ast
	else:
		return render(request, 'register.html', {})
#------------------------------------------------------------------------------#
def login_view(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				auth_login(request, user)
				messages.success(request, 'با موفقیت وارد سیستم شدید.')
				return redirect('login') # go to home
			else:
				messages.error(request, 'در حال حاضر اکانت شما فعال نمی باشد')
				return redirect('register')
		else:
			messages.error(request, 'یوزرنیم یا پسورد وارد شده اشتباه است')
			return redirect('login')
	else:
		return render(request, 'login.html', {})
#------------------------------------------------------------------------------#
@login_required
def logout_view(request):
	django_logout(request)
	messages.success(request, 'با موفقیت از سیستم خارج شدید.')
	return redirect('login')
#------------------------------------------------------------------------------#
def password_reset(request):
	# karbar email khod ra vared karde ast
	if 'resetPassword' in request.POST:
		if User.objects.filter(email=request.POST['email']).exists():
			userid = User.objects.get(email=request.POST['email']).id
			email = User.objects.get(id=userid).email
			username = User.objects.get(id=userid).username
			now = datetime.now()
			this_user = User.objects.get(email=email)
			token = password_reset_token(username, email, userid)
			passresetcode = Passwordresetcodes(
			user=this_user, code=token, time=now)
			passresetcode.save()
			messages.success(request, "<a href=\"{}?token={}&id={}\">\
			لینک رو به رو</a>".format(request.build_absolute_uri\
			('/account/begin_password_reset/'), token, userid))
			return render (request, 'password_reset.html', {})
		else:
			messages.error(request, 'کاربری با این مشخصات پیدا نشد')
			return redirect('pasword_reset')


	# karbar email ersal shode ra click karde ast
	elif 'token' in request.GET and 'id' in request.GET:
		code = request.GET['token']
		userid = request.GET['id']
		thisuser = get_object_or_404(User, id=userid)
		token = get_object_or_404(Passwordresetcodes, user=thisuser).code
		if code == token and thisuser.is_active == True:
			now = datetime.now()
			utc = pytz.UTC
			dt = now.replace(tzinfo=utc) - get_object_or_404(Passwordresetcodes, user=thisuser).time.replace(tzinfo=utc)
			dt= dt.days
			if dt < 1:
				request.session['requested_user'] = userid
				return render(request, 'password_reset_confirm.html', {})
			else:
				Passwordresetcodes.objects.get(user=thisuser).delete()
				messages.error(request, 'زمانه استفاده از توکن گذشته است. لطفا\
				مجددا درخواست نمایید.')
				return redirect('pasword_reset')
		elif code == token and thisuser.is_active == False:
			messages.warning(request, 'متاسفانه در حال حاضر این اکانت\
			غیر فعال می باشد. لطفا جهت پیگیری با مدیریت سایت در ارتباط\
			باشید.')
		else:
			messages.error(request, 'متاسفانه مشکلی پیش آمده است. لطفا \
			دوباره امتحان کنید.')
			auth_login(request, thisuser)
			return redirect('pasword_reset')

	# karbar form password jadid ra por karde ast
	elif 'passconfirm' in request.POST:
		password = request.POST['password']
		password2 = request.POST['password2']
		userid = request.session.get('requested_user')
		thisuser = get_object_or_404(User, id=userid)
		Passwordresetcodes.objects.get(user=thisuser).delete()
		if password == password2:
			password2 = None
			thisuser.set_password(request.POST['password'])
			thisuser.save()
			messages.success(request, "پسورد شما با موفقیت تغییر پیدا کرد.")
			return redirect('login')
		else:
			messages.success(request, "پسوردهای وارد شده با هم برابر نیست.")
			return redirect(request.META.get('HTTP_REFERER'))

	# karbar avalin bar ast be safhe register amade ast
	else:
		return render(request, 'password_reset.html', {})
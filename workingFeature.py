This is the pythonFile 

from django.http import HttpResponse
from .forms import createUserForm
from django.shortcuts import render,redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .token import account_activation_token
from django.contrib.auth.models import User

from django.contrib.auth import login, logout, authenticate

from .forms import loginForm, userUpdateForm

def register(request):
    form = createUserForm()
    if request.method =="POST":
        form = createUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            
            current_site = get_current_site(request)
            #Email verification logic
            subject = 'Paradox Pvt Ltd! Verify your email to activate your account'
            message = render_to_string('users/email-verification.html', {
                'user': user,
                'domain': current_site.domain,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject=subject, message=message)
            return redirect('email-verification-sent')
    return render(request,'users/register.html',{'form':form})


def email_verification(request,uidb64,token):
    unique_id = force_str(urlsafe_base64_decode(uidb64))
    user = User.objects.get(id=unique_id)
    if user and account_activation_token.check_token(user,token):
        user.is_active = True
        user.save()
        return redirect('email-verification-success')
    else:
        return redirect('email-verification-failed')
    
    

def email_verification_sent(request):
    return render(request, 'users/email-verification-sent.html')

def email_verification_success(request):
    return render(request, 'users/email-verification-success.html')

def email_verification_failed(request):
    return render(request, 'users/email-verification-failed.html')


def loginPage(request):
    form = loginForm
    if request.method =="POST":
        form = loginForm(request,data=request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request,username=username,password=password)
            #authenticate method returns the user by checking the username and 
            # password exits in our application.
            if user is not None:
                login(request,user)
            return redirect('basePage')
    return render(request,'users/login.html',{'form':form})


def logoutPage(request):
    logout(request)
    return redirect('basePage')
        
def profilePage(request):
    if not request.user.is_authenticated:
        return redirect('basePage')
    else:
        user_form = userUpdateForm(instance=request.user)
        if request.method=="POST":
            user_form = userUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                return redirect('basePage')
        return render(request, 'users/profile.html',{'form':user_form})
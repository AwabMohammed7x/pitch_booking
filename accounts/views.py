from django.shortcuts import redirect, render
from accounts.form import UserLoginForm, UserRegisterForm ,UserPasswordChange,UserupdateForm,ProfileForm
from django.contrib import messages 
from django.contrib.auth import authenticate, login ,logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required

# Create your views here.
def register(request):
    # 1. منع المستخدم المسجل أصلاً من الدخول لصفحة التسجيل
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.')
        return redirect('home')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # 2. الحفظ في قاعدة البيانات (أول وأهم خطوة)
            user = form.save() 
            
            # 3. استخراج البيانات بعد ما اتأكدنا إنها سليمة
            username = form.cleaned_data.get('username')  
            # في فورمات ديجانجو الافتراضية، حقل الباسورد الأول اسمه password1
            password = form.cleaned_data.get('password1')  
            
            # 4. المصادقة وتسجيل الدخول للمستخدم اللي لسه محفوظ هسي
            auth_user = authenticate(username=username, password=password)
            if auth_user is not None:
                login(request, auth_user)
            
            # 5. رسالة النجاح والتوجيه
            messages.success(request, 'Your account has been created successfully. You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
        
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.user.is_authenticated:
        messages.error(request, 'You are already logged in.')
        return redirect('home')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user :
                login(request, user)
                url_next=request.GET.get('next')
                if url_next:
                    messages.success(request, 'You have successfully logged in.')
                    return redirect(url_next)
                else:
                    messages.success(request, 'You have successfully logged in.')
                    return redirect('home')
            else:
                messages.error(request, 'Invalid username or password. Please try again.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.success(request,'loging out successfully... ')
    return redirect('home')
    
@login_required(login_url='login')
def change_password(request):
    if request.method =='POST':
        form=UserPasswordChange(user=request.user,data=request.POST)
        if form.is_valid():
            form.save()
            # update the session with the new password so the user isn't logged out
            update_session_auth_hash(request, request.user)
            
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('home')
    else:
        form=UserPasswordChange(request.user)

    return render(request, 'accounts/change_pass.html', {'form': form})

@login_required(login_url='login')
def profile(request):
    if request.method=='POST':
        u_form=UserupdateForm(request.POST,instance=request.user)

        p_form=ProfileForm(request.POST,request.FILES,instance=request.user.profile)
        
        # 1. فحصنا الفورمتين مع بعض بشكل سليم بالملّي 🚨
        if u_form.is_valid() and p_form.is_valid(): 
            
            u_form.save() # حفظ بيانات الـ User (صح ومباشر)
            p_form.save() # حفظ بيانات الـ Profile (صح ومباشر)

            messages.success(request, 'Updated Profile successfully')
            
            # 2. أضفنا الـ return ومررنا الـ pk عشان الرابط الديناميكي ما يضرب 🚨
            return redirect('profile')
    else:
        u_form=UserupdateForm(instance=request.user)

        p_form=ProfileForm(request.FILES,instance=request.user.profile)
    context={
        'u_form':u_form,
        'p_form':p_form
    }
    return render(request, 'accounts/profile.html' ,context)


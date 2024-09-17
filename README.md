# WEEK 12 - Using the Django authentication system

[Doc](https://docs.djangoproject.com/en/5.1/topics/auth/default/)

Django นั้นมีระบบการทำ authentication และ authorization built-in มาให้เราใช้งานได้เลย และยัง support การ customization ที่ค่อนข้างลึกมากๆ

## User objects

สังเกตดูเมื่อเราทำการ migrate ตารางฐานข้อมูล Django จะ migrate ตาราง `auth_user` มาให้เลย ซึ่งจะเป็นตารางที่ใช้ในการเก็บข้อมูล user ของระบบ ซึ่งมี field ดังนี้

- username
- first_name
- last_name
- email
- password
- groups (M2M to model `Group`)
- user_permissions (M2M to model `Permission`)
- is_staff (สามารถเข้าใช้งาน Django Admin ได้)
- is_superuser (สามารถเข้าใช้งาน Django Admin ได้ และ มีทุก permissions)
- is_active
- last_login
- date_joined

### Creating users

เราสามารถใช้ helper function `create_user()` ในการสร้าง user ได้

```python
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")

# At this point, user is a User object that has already been saved
# to the database. You can continue to change its attributes
# if you want to change other fields.
>>> user.last_name = "Lennon"
>>> user.save()
```

### Creating superusers

การสร้าง superuser จะต้องทำโดยใช้ command:

```sh
$ python manage.py createsuperuser --username=joe --email=joe@example.com
```

### Changing passwords

Password ที่ถูกเก็บในตาราง `auth_user` จะถูก hash เอาไว้ดังนั้นเราจะไม่สามารถเข้าไปอ่าน หรือ แก้ไข password โดยตรงในฐานข้อมูลได้

ในกรณีที่ต้องการเปลี่ยน password สามารถทำได้ 2 วิธีคือ

1. ใช้ command `manage.py changepassword *username*` ใน command line
2. ใช้ method `set_password()`

```python
>>> from django.contrib.auth.models import User
>>> u = User.objects.get(username="john")
>>> u.set_password("new password")
>>> u.save()
```

3. ไปทำการเปลี่ยน password ผ่าน UI ใน Django Admin

### Authenticating users

ใช้ function `authenticate()` ในการตรวจสอบ username และ password ได้ โดยจะได้รับ instance ของ `User` ที่ทำการตรวจสอบสำเร็จกลับมา

```python
from django.contrib.auth import authenticate

user = authenticate(username="john", password="secret")
if user is not None:
    # Success
    ...
else:
    # Fail
    ...
```

## Authentication in web requests

หลังจาก user ทำการ login (หรือ authenticate) แล้ว ในทุกๆ web request Django จะทำการแนบ instance ของ `User` มาให้ด้วย (ซึ่งถูกเก็บอยู่ใน session) ใน `request.user`

แต่ถ้า user ยังไม่ได้ login (หรือก็คือยังไม่ได้ถูก authenticate) `request.user` จะเป็น instace ของ AnonymousUser

**AnonymousUser** object

- id is always None.
- username is always the empty string.
- is_anonymous is True instead of False.
- is_authenticated is False instead of True.
- is_staff and is_superuser are always False.
- is_active is always False.
- groups and user_permissions are always empty.
- set_password(), check_password(), save() and delete() raise NotImplementedError.

โดยเราสามารถเช็คได้ว่า user นั้น authenticate แล้วหรือยังได้โดยตรวจสอบที่ค่าของ `user.is_authenticated`

```python
if request.user.is_authenticated:
    # Do something for authenticated users.
    ...
else:
    # Do something for anonymous users.
    ...
```

### How to log a user in

Django มี function `login()` ให้เราใช้งานดังตัวอย่าง

```python
from django.contrib.auth import authenticate, login


def my_view(request):
    username = request.POST["username"]
    password = request.POST["password"]
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        ...
    else:
        # Return an 'invalid login' error message.
        ...
```

### How to log a user out

เมื่อเราทำการ `logout()` session ของ user จะถูก clear ทั้งหมด

```python
from django.contrib.auth import logout


def logout_view(request):
    logout(request)
    # Redirect to a success page.
```

### Limiting access to logged-in users

เราสามารถกำหนดได้ว่า view ไหนให้เข้าได้เฉพาะ user ที่ logged-in แล้ว (authenticated users) โดยสามารถทำได้ 2 วิธี

```python
# The raw way
from django.conf import settings
from django.shortcuts import redirect


def my_view(request):
    if not request.user.is_authenticated:
        return redirect(f"{settings.LOGIN_URL}?next={request.path}")
```

```python
# The login_required decorator
from django.contrib.auth.decorators import login_required


@login_required
def my_view(request): ...
```

โดย `login_required()` จะทำสิ่งต่อไปนี้

- ถ้า user ยังไม่ได้ login จะทำการ redirect user ไปที่ `setting.LOGIN_URL` และส่ง absolute path ไปด้วยในตัวแปร `next` เช่น **/accounts/login/?next=/polls/3/**
- ถ้า user login แล้วก็จะเข้าไปทำงานใน view ตามปกติ

```python
# เราสามารถกำหนด login_url ที่จำทำการ redirect user ไปได้ด้วยการกำหนด parameter "login_url"
from django.contrib.auth.decorators import login_required


@login_required(login_url="/accounts/login/")
def my_view(request): ...
```

และสำหรับ class-based view เราจะใช้ `LoginRequiredMixin` สำหรับการจำกัดว่า class View นั้นๆ จะสามารถเข้าถึงได้เฉพาะ user ที่ login แล้วเท่านั้น

```python
from django.contrib.auth.mixins import LoginRequiredMixin


class MyView(LoginRequiredMixin, View):
    login_url = "/login/"
```

### Built-in forms

Django ยังมี provide class `Form` สำหรับการ authenticate ให้ใช้งานหลายตัว ซึ่งตัวที่นิยมใช้งานได้แก่

*class* **AuthenticationForm**

เป็น form สำหรับ login user ซึ่งมี field ทั้งหมด 2 fields:

- username
- password

```python
# AuthenticationForm - source
class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """

    username = UsernameField(widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
```

ตัวอย่างการใช้งาน

```python
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm

def signin(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            return redirect('home')  
    else:
        form = AuthenticationForm()
    return render(request,'signin.html', {"form":form})
```

*class* **UserCreationForm**

เป็น ModelForm สำหรับสร้าง user ใหม่ซึ่งมี field 3 fields:

- username
- password1
- password2 (password1 และ password2 จะต้อง match กัน)

```python
from django.shortcuts import render  
from django.contrib.auth.forms import UserCreationForm
  
def register(request):  
    if request.POST == 'POST':  
        form = UserCreationForm(request.POST)  
        if form.is_valid():  
            form.save()  
    messages.success(request, 'Account created successfully')  
  
    else:  
        form = UserCreationForm()  
    context = {  
        'form':form  
    }  
    return render(request, 'register.html', context)  
```

*class* **PasswordChangeForm**

```python
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important for keeping the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})
```

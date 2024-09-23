# WEEK 12 Tutorial

## Setting up the "Booking Application"

เรามาลองปรับแก้ไข website **Room Booking** ของเราให้เป็นดังนี้

- จำเป็นจะต้อง login จึงจะสามารถใช้งานระบบได้
- user ผู้ใช้งานจะมี 2 group ได้แก่ staff และ admin โดย
    - สำหรับ user ที่เป็น staff จะสามารถสร้าง Booking และดู booking list ได้เท่านั้น
    - สำหรับ user ที่เป็น admin จะสามารถแก้ไขและยกเลิก booking และดู booking list แต่ไม่สามารถสร้าง booking ได้
- สามารถ logout ได้

เรามาเริ่มทำ tutorial กันเถอะ

1. สร้าง project "week12_tutorial" และ app "bookings"
2. แก้ไข `settings.py` โดยเพิ่ม app "bookings" และตั้งค่า DATABASES
3. เพิ่ม code นี้ใน `bookings/models.py`

```python
from django.db import models

class Staff(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class RoomType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    capacity = models.IntegerField()
    description = models.TextField(blank=True)
    room_types = models.ManyToManyField(RoomType, related_name='rooms', blank=True)

    def __str__(self):
        return f'Room {self.number}: {self.name}'


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    staff = models.ForeignKey(Staff, on_delete=models.PROTECT)
    email = models.EmailField(null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    purpose = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'Booking for {self.room} from {self.start_time} to {self.end_time}'
```

4. สร้างฐานข้อมูล "bookings" ทำการ makemigrations และ migration
5. import ข้อมูลใน "bookings.sql"
6. เพิ่ม code ใน `bookings/views.py`

```python
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q

from bookings.models import Booking
from bookings.forms import BookingForm

class BookingList(View):

    def get(self, request):
        query = request.GET
        bookings = Booking.objects.order_by("start_time")

        if query.get("search"):
            bookings = bookings.filter(
                Q(room__name__icontains=query.get("search")) | 
                Q(staff__name__icontains=query.get("search"))
            )

        return render(request, "booking-list.html", {
            "bookings": bookings
        })


class BookingCreate(View):

    def get(self, request):
        form = BookingForm()
        return render(request, "booking.html", {
            "form": form,
        })

    def post(self, request):
        form = BookingForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('booking-list')

        return render(request, "booking.html", {
            "form": form
        })

class BookingUpdate(View):

    def get(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        form = BookingForm(instance=booking)
        return render(request, "booking.html", {
            "form": form,
        })

    def post(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        form = BookingForm(request.POST, instance=booking)

        if form.is_valid():
            form.save()
            return redirect('booking-list')

        return render(request, "booking.html", {
            "form": form
        })


class BookingDelete(View):

    def get(self, request, booking_id):
        booking = Booking.objects.get(pk=booking_id)
        booking.delete()

        return redirect("booking-list")
```

7. เพิ่ม code ใน `bookings/urls.py` และ `week12_tutorial/urls.py`

```python
# bookings/urls.py
from django.urls import path

from bookings import views

urlpatterns = [
    path("", views.BookingList.as_view(), name="booking-list"),
    path("create/", views.BookingCreate.as_view(), name="booking-create"),
    path("update/<int:booking_id>", views.BookingUpdate.as_view(), name="booking-update"),
    path("delete/<int:booking_id>", views.BookingDelete.as_view(), name="booking-delete"),
]
```

```python
# week12_tutorial/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bookings/", include("bookings.urls")),
]
```

8. เพิ่ม code ใน `bookings/forms.py`

```python
from django.forms import ModelForm, SplitDateTimeField
from django.forms.widgets import Textarea, TextInput, SplitDateTimeWidget
from django.core.exceptions import ValidationError

from bookings.models import Booking

class BookingForm(ModelForm):
    start_time = SplitDateTimeField(widget=SplitDateTimeWidget(
                date_attrs={"class": "input", "type": "date"},
                time_attrs={"class": "input", "type": "time"}
            ))
    end_time = SplitDateTimeField(widget=SplitDateTimeWidget(
                date_attrs={"class": "input", "type": "date"},
                time_attrs={"class": "input", "type": "time"}
            ))

    class Meta:
        model = Booking
        fields = [
            "room", 
            "staff", 
            "email", 
            "start_time", 
            "end_time", 
            "purpose"
        ]
        widgets = {
            "email": TextInput(attrs={"class": "input"}),
            "purpose": Textarea(attrs={"rows": 5, "class": "textarea"})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        room = cleaned_data.get("room")
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time < start_time:
            raise ValidationError(
                    "End time cannot be before start time"
                )
        bookings = Booking.objects.filter(
            start_time__lte=end_time, 
            end_time__gte=start_time, 
            room=room
        )
        if bookings.count() > 0:
            raise ValidationError(
                    "This room has already been booked for the selected time"
                )

        return cleaned_data
```

9. เพิ่ม code ใน `templates/booking.html` และ `templates/booking-list.html`

```html
<!--templates/booking.html-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Room Booking</title>
    <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css"
        >
</head>
<body>
    <section class="section">
        <h1 class="title" id="title">Add New Booking/Edit Booking</h1>
    </section>
    <div class="container pl-5">
        {{ form.non_field_errors }}
        <form action="{% url 'booking-create' %}" method="POST">
            {% csrf_token %}
            <div class="field">
                {{ form.room.errors }}
                <label class="label" for="{{ form.room.id_for_label }}">Room to book</label>
                <div class="control">
                    <div class="select">
                        {{ form.room }}
                    </div>
                </div>
                </div>

            <div class="field">
                {{ form.staff.errors }}
                <label class="label" for="{{ form.staff.id_for_label }}">Booked for</label>
                <div class="control">
                    <div class="select">
                        {{form.staff}}
                    </div>
                </div>
            </div>
            <div class="field">
                {{ form.email.errors }}
                <label class="label" for="{{ form.email.id_for_label }}">Email</label>
                <div class="control">
                    {{form.email}}
                </div>
            </div>
            <div class="field">
                {{ form.purpose.errors }}
                <label class="label" for="{{ form.purpose.id_for_label }}">Purpose</label>
                <div class="control">
                    {{form.purpose}}
                </div>
            </div>
            <div class="field">
                {{ form.start_time.errors }}
                <label class="label" for="{{ form.start_time.id_for_label }}">Start time</label>
                <div class="control">
                    <div class="columns">
                        <div class="column">
                            {{ form.start_time }}
                        </div>
                        <div class="column"></div>
                      </div>
                </div>
            </div>
            <div class="field">
                {{ form.end_time.errors }}
                <label class="label" for="{{ form.end_time.id_for_label }}">End time</label>
                <div class="control">
                    <div class="columns">
                        <div class="column">
                            {{ form.end_time }}
                        </div>
                        <div class="column"></div>
                        <div class="column"></div>
                      </div>
                </div>
            </div>
            <div class="field is-grouped">
                <div class="control">
                    <input type="submit" class="button is-link">
                </div>
                <div class="control">
                    <a class="button is-danger" href="{% url 'booking-list' %}">Back</a>
                </div>
            </div>
        </form>
    </div>
</body>
</html>
```

```html
<!--templates/booking-list.html-->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking List</title>
    <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css"
    >
</head>
<body>
    <section class="section">
        <h1 class="title" id="title">Booking List</h1>
    </section>
    <div class="container">
        <form action="{% url 'booking-list' %}">
            <div class="field">
                <label class="label">Name</label>
                <div class="control">
                    <div class="columns">
                        <div class="column">
                            <input class="input" type="text" name="search" placeholder="Search room name / staff name">
                        </div>
                        <div class="column">
                            <input class="button" type="submit" value="Search">
                            <a class="button is-success" href="{% url 'booking-create' %}">Add New Booking</a>
                        </div>
                    </div>
                </div>
              </div>
        </form>
        <br/>
        <table class="table" id="datatable">
            <thead>
                <tr>
                    <th>Room</th>
                    <th>Staff</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Purpose</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for booking in bookings %}
                <tr>
                    <td>{{booking.room.name}}</td>
                    <td>{{booking.staff.name}}</td>
                    <td>{{booking.start_time|date}}</td>
                    <td>{{booking.start_time|time:"H:i"}} - {{booking.end_time|time:"H:i"}}</td>
                    <td>{{booking.purpose}}</td>
                    <td>
                        <a class="button is-info" href="{% url 'booking-update' booking.id %}">Edit Booking</a>
                        <a class="button is-warning" href="{% url 'booking-delete' booking.id %}">Cancel Booking</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
```

10. run command `python manage.py runserver` และทดสอบว่าระบบสามารถใช้งานได้

## Let's create groups and users in Django Admin

ก่อนอื่นเรามาสร้าง superuser สำหรับ login เข้า Django Admin เพื่อไปสร้าง groups และ assign permissions กัน

```sh
$ python manage.py createsuperuser
```

จากนั้นก็ใช้ username และ password ที่สร้างไป login ใน Django Admin

- ทำการสร้าง `Group` 2 groups ได้แก่ "Staff" และ "Admin"
- ทำการผูก `Permission` ดังนี้

    - **Staff**
        - `bookings.view_booking`
        - `bookings.add_booking`
    - **Admin**
        - `bookings.view_booking`
        - `bookings.change_booking`
        - `bookings.delete_booking`


- ทำการสร้าง `User` 2 users ได้แก่ "staff1" (อยู่ group "Staff") และ "admin1" (อยู่ group "Admin")

## Apply `LoginRequiredMixin` to the views

เราจะทำการ extend `LoginRequiredMixin` สำหรับทุก class View

```python
class BookingList(LoginRequiredMixin, View):
    login_url = '/login/'
    ...

class BookingCreate(LoginRequiredMixin, View):
    login_url = '/login/'
    ...

class BookingUpdate(LoginRequiredMixin, View):
    login_url = '/login/'
    ...

class BookingDelete(LoginRequiredMixin, View):
    login_url = '/login/'
    ...
```

ถ้าเราพยายามเข้า View พวกนี้เราจะไม่สามารถเข้าใช้งานได้แล้วเนื่องจากยังไม่ได้ login

## The login page

เราจะต้องมาทำหน้า login และ logout กัน

เราจะใช้งาน AuthenticationForm สำหรับ login user กันนะครับ

ก่อนอื่นเรามาสร้างหน้า login กันก่อน `bookings/templates/login.html`

```html
<!-- login.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link
        rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/bulma@1.0.2/css/bulma.min.css"
        >
</head>
<body>
    <section class="section">
        <h1 class="title" id="title">Login</h1>
    </section>
    <div class="container pl-5">
        {{ form.non_field_errors }}
        <form action="{% url 'login' %}" method="POST">
            {% csrf_token %}
            <div class="field">
                {{ form.username.errors }}
                <label class="label" for="{{ form.username.id_for_label }}">Username</label>
                <div class="control">
                    {{form.username}}
                </div>
            </div>
            <div class="field">
                {{ form.password.errors }}
                <label class="label" for="{{ form.password.id_for_label }}">Password</label>
                <div class="control">
                    {{form.password}}
                </div>
            </div>
            <div class="field is-grouped">
                <div class="control">
                    <input type="submit" class="button is-link" value="LOGIN">
                </div>
            </div>
        </form>
    </div>
</body>
</html>
```

จากนั้นไปเพิ่ม class-based view Login(View) และ Logout(View) ใน `bookings/views.py`

```python
...
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
...


class Login(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'login.html', {"form": form})
    
    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request,user)
            return redirect('booking-list')  

        return render(request,'login.html', {"form":form})


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('login')

...
```

ลอง login ดูจะสามารถเข้าใช้งาน website ได้แล้ว เย้ๆๆๆ

## Let's add permission guards to the views

เราจะใช้งาน `PermissionRequiredMixin` กัน ดังนั้น extend เพิ่มเข้าไปในแต่ละ view

```python
...
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
...

class BookingList(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ["bookings.view_booking"]
    ...

class BookingCreate(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ["bookings.add_booking"]
    ...

class BookingUpdate(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ["bookings.change_booking"]
    ...

class BookingDelete(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = ["bookings.delete_booking"]
    ...
```

ถ้าเรา login เป็น "staff1" เราจะไม่สามารถกด "Edit Booking" และ "Cancel Booking" ได้ จะได้หน้า 403 Forbidden ซึ่งหมายถึงว่าเราไม่มี permission ในการเข้าใช้งาน view นั้นๆ

ถ้า "Staff" ไม่ควรกดได้เราก็ซ่อนปุ่มไปเลยน่าจะดีกว่า เราไปแก้ไขใน `booking-list.html` กัน

```html
<div class="column">
    <input class="button" type="submit" value="Search">
    {% if perms.bookings.add_booking %}
        <a class="button is-success" href="{% url 'booking-create' %}">Add New Booking</a>
    {% endif %}
</div>
...
<td>
    {% if perms.bookings.change_booking %}
    <a class="button is-info" href="{% url 'booking-update' booking.id %}">Edit Booking</a>
    {% endif %}
    {% if perms.bookings.delete_booking %}
    <a class="button is-warning" href="{% url 'booking-delete' booking.id %}">Cancel Booking</a>
    {% endif %}
</td>
```

**Hint:** ถ้าจะเช็คว่า user นั้น login (is_authenticated) ใน template สามารถทำได้โดย

```html
{% if user.is_authenticated %}
    <p>Welcome, {{ user.username }}. Thanks for logging in.</p>
{% else %}
    <p>Welcome, new user. Please log in.</p>
{% endif %}
```

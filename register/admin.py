from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

admin.peppolDEMO.register(User, UserAdmin)

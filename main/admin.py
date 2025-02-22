from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from main.models import User
# Register your models here.


class UserModelAdmin(UserAdmin):
    model = User
    list_display = ["id", "email", "name"]
    list_filter = ["is_superuser"]
    ordering= ["email"]
    filter_horizontal=[]

admin.site.register(User,UserModelAdmin)


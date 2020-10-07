from django.contrib import admin

# Register your models here.
from .models import BepUser, Session, Book, Order

admin.site.register(BepUser)
admin.site.register(Session)
admin.site.register(Book)
admin.site.register(Order)

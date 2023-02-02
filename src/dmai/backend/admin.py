from django.contrib import admin

from .models import Inference, Data, DataAPI

# Register your models here.

admin.site.register(Inference)
admin.site.register(Data)
admin.site.register(DataAPI)
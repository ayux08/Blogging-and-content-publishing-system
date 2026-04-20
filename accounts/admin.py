from django.contrib import admin
from .models import tbl_user, tbl_contact, tbl_notifications

admin.site.register(tbl_user)
admin.site.register(tbl_contact)
admin.site.register(tbl_notifications)

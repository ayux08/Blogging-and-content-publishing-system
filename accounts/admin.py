from django.contrib import admin
from .models import tbl_user, tbl_contact, tbl_notifications


@admin.register(tbl_user)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'email', 'role', 'status', 'created_at')
    list_filter = ('role', 'status')
    search_fields = ('name', 'username', 'email')
    list_editable = ('role', 'status')


@admin.register(tbl_contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'mobile', 'created_at')
    search_fields = ('name', 'email')


@admin.register(tbl_notifications)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')

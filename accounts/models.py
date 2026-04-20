from django.db import models


class tbl_user(models.Model):
    """Core user model for all roles (admin, author, reader)."""
    name = models.CharField(max_length=80)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True, max_length=60)
    password = models.CharField(max_length=128)
    role = models.CharField(max_length=20, default='reader',
                            choices=[('admin', 'Admin'), ('author', 'Author'), ('reader', 'Reader')])
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.role})"


class tbl_contact(models.Model):
    """Contact form submissions."""
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=60)
    mobile = models.CharField(max_length=15, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


class tbl_notifications(models.Model):
    """System notifications for users."""
    user_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, default='Notification')
    message = models.TextField()
    notification_type = models.CharField(max_length=30, default='info',
                                         choices=[('info', 'Info'), ('like', 'Like'), ('comment', 'Comment'),
                                                  ('follow', 'Follow'), ('post', 'New Post'), ('system', 'System')])
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user_id.name}: {self.title}"

    class Meta:
        ordering = ['-created_at']

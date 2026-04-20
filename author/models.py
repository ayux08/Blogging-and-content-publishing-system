from django.db import models
from accounts.models import tbl_user


class tbl_authors(models.Model):
    """Author profile extending the user model."""
    user_id = models.OneToOneField(tbl_user, on_delete=models.CASCADE, related_name='author_profile')
    bio = models.TextField(blank=True, default='')
    profile_image = models.ImageField(upload_to='authors/profiles/', blank=True, null=True)
    website = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Author: {self.user_id.name}"


class tbl_categories(models.Model):
    """Blog post categories."""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class tbl_tags(models.Model):
    """Tags for blog posts."""
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class tbl_posts(models.Model):
    """Blog posts created by authors."""
    author_id = models.ForeignKey(tbl_authors, on_delete=models.CASCADE, related_name='posts')
    category_id = models.ForeignKey(tbl_categories, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    excerpt = models.TextField(blank=True, default='', max_length=500)
    featured_image = models.ImageField(upload_to='posts/featured/', blank=True, null=True)
    status = models.BooleanField(default=False)  # False=Pending/Draft, True=Published
    is_submitted = models.BooleanField(default=False)  # True=Pending Review, False=Draft
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Posts"


class tbl_post_tags(models.Model):
    """Many-to-many relationship between posts and tags."""
    post_id = models.ForeignKey(tbl_posts, on_delete=models.CASCADE, related_name='post_tags')
    tag_id = models.ForeignKey(tbl_tags, on_delete=models.CASCADE)


class tbl_media(models.Model):
    """Uploaded media files (images, videos, etc.)."""
    file_path = models.FileField(upload_to='uploads/')
    file_name = models.CharField(max_length=200, blank=True)
    file_type = models.CharField(max_length=20, blank=True)
    uploaded_by = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='media_files')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name or str(self.file_path)

    def save(self, *args, **kwargs):
        if not self.file_name and self.file_path:
            self.file_name = self.file_path.name.split('/')[-1]
        if not self.file_type and self.file_path:
            ext = self.file_path.name.split('.')[-1].lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']:
                self.file_type = 'image'
            elif ext in ['mp4', 'webm', 'avi', 'mov']:
                self.file_type = 'video'
            else:
                self.file_type = 'file'
        super().save(*args, **kwargs)


class tbl_post_images(models.Model):
    """Multiple images for a single post."""
    post_id = models.ForeignKey(tbl_posts, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='posts/images/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

from django.db import models
from accounts.models import tbl_user
from author.models import tbl_posts


class tbl_readers(models.Model):
    """Reader profile extending the user model."""
    user_id = models.OneToOneField(tbl_user, on_delete=models.CASCADE, related_name='reader_profile')
    profile_image = models.ImageField(upload_to='readers/profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reader: {self.user_id.name}"


class tbl_comments(models.Model):
    """Comments on blog posts."""
    post_id = models.ForeignKey(tbl_posts, on_delete=models.CASCADE, related_name='comments')
    user_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='comments')
    parent_id = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    comment_text = models.TextField()
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user_id.name} on {self.post_id.title}"

    class Meta:
        ordering = ['-created_at']


class tbl_likes(models.Model):
    """Likes on blog posts."""
    post_id = models.ForeignKey(tbl_posts, on_delete=models.CASCADE, related_name='likes')
    user_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post_id', 'user_id')


class tbl_bookmarks(models.Model):
    """Bookmarked posts by users."""
    user_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='bookmarks')
    post_id = models.ForeignKey(tbl_posts, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'post_id')


class tbl_post_views(models.Model):
    """Track post views per user."""
    post_id = models.ForeignKey(tbl_posts, on_delete=models.CASCADE, related_name='views')
    user_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='post_views')
    viewed_at = models.DateTimeField(auto_now_add=True)


class tbl_shares(models.Model):
    """Track post shares."""
    post_id = models.ForeignKey(tbl_posts, on_delete=models.CASCADE, related_name='shares')
    user_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='shares')
    platform = models.CharField(max_length=30, default='link',
                                choices=[('twitter', 'Twitter'), ('facebook', 'Facebook'),
                                         ('linkedin', 'LinkedIn'), ('whatsapp', 'WhatsApp'),
                                         ('link', 'Copy Link')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id.name} shared {self.post_id.title} on {self.platform}"


class tbl_follows(models.Model):
    """Track user follows (reader follows author)."""
    follower_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='following')
    following_id = models.ForeignKey(tbl_user, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower_id', 'following_id')

    def __str__(self):
        return f"{self.follower_id.name} follows {self.following_id.name}"

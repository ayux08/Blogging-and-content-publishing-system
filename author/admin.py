from django.contrib import admin
from .models import tbl_authors, tbl_categories, tbl_tags, tbl_posts, tbl_post_tags, tbl_media, tbl_post_images

admin.site.register(tbl_authors)
admin.site.register(tbl_categories)
admin.site.register(tbl_tags)
admin.site.register(tbl_posts)
admin.site.register(tbl_post_tags)
admin.site.register(tbl_media)
admin.site.register(tbl_post_images)

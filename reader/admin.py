from django.contrib import admin
from .models import tbl_readers, tbl_comments, tbl_likes, tbl_bookmarks, tbl_post_views, tbl_shares

admin.site.register(tbl_readers)
admin.site.register(tbl_comments)
admin.site.register(tbl_likes)
admin.site.register(tbl_bookmarks)
admin.site.register(tbl_post_views)
admin.site.register(tbl_shares)

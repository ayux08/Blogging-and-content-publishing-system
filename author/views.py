from django.shortcuts import render, redirect, get_object_or_404
from .models import tbl_authors, tbl_posts, tbl_categories, tbl_tags, tbl_post_tags, tbl_media, tbl_post_images
from reader.models import tbl_comments, tbl_post_views, tbl_likes
from accounts.models import tbl_user, tbl_notifications


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def require_author(request):
    if not request.session.get('user_id'):
        return redirect('/accounts/login/')
    role = request.session.get('user_role', 'reader').lower()
    if role not in ['author', 'admin']:
        return redirect('/reader/')
    return None


def get_author(request):
    uid = request.session.get('user_id')
    if not uid:
        return None
    try:
        user = tbl_user.objects.get(id=uid)
        author = tbl_authors.objects.get(user_id=user)
        return author
    except (tbl_user.DoesNotExist, tbl_authors.DoesNotExist):
        return None


def get_session_context(request):
    uid = request.session.get('user_id')
    notif_count = 0
    if uid:
        notif_count = tbl_notifications.objects.filter(user_id__id=uid, is_read=False).count()
    return {
        'user_id': uid,
        'user_name': request.session.get('user_name', 'Guest'),
        'user_role': request.session.get('user_role', 'author'),
        'user_username': request.session.get('user_username', ''),
        'notif_count': notif_count,
    }


# ─── 6.2.2 AUTHOR DASHBOARD ─────────────────────────────────────────────────

def dashboard(request):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "dashboard"})
    if author:
        posts = tbl_posts.objects.filter(author_id=author)
        ctx.update({
            "total_posts": posts.count(),
            "published": posts.filter(status=True).count(),
            "drafts_count": posts.filter(status=False).count(),
            "total_comments": tbl_comments.objects.filter(post_id__in=posts).count(),
            "total_views": tbl_post_views.objects.filter(post_id__in=posts).count(),
            "total_likes": tbl_likes.objects.filter(post_id__in=posts).count(),
            "recent_posts": posts.order_by("-id")[:5],
            "recent_comments": tbl_comments.objects.filter(post_id__in=posts).order_by("-id")[:5],
            "author": author,
        })
    return render(request, "author/dashboard.html", ctx)


# ─── 6.2.3 BLOG CREATION MODULE ──────────────────────────────────────────────

def create_post(request):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "create"})

    if request.method == "POST" and author:
        title = request.POST.get("title", "").strip()
        content = request.POST.get("content", "").strip()
        cat_id = request.POST.get("category")
        status_val = request.POST.get("status", "draft")
        tags_str = request.POST.get("tags", "")
        images = request.FILES.getlist("images")

        if not title or not content:
            ctx["categories"] = tbl_categories.objects.all()
            ctx["error"] = "Title and content are required."
            return render(request, "author/create.html", ctx)

        try:
            category = tbl_categories.objects.get(id=cat_id)
        except tbl_categories.DoesNotExist:
            category = tbl_categories.objects.first()

        # Auto-generate excerpt from content
        import re
        plain_text = re.sub(r'<[^>]+>', '', content).strip()
        excerpt = plain_text[:200] + "..." if len(plain_text) > 200 else plain_text

        post = tbl_posts(
            author_id=author,
            category_id=category,
            title=title,
            content=content,
            excerpt=excerpt,
            status=False,  # Always False until Admin approves
            is_submitted=(status_val == "publish"),
        )
        # First image = featured image, rest = additional
        if images:
            post.featured_image = images[0]
        post.save()

        # Handle tags
        if tags_str:
            for tag_name in tags_str.split(","):
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = tbl_tags.objects.get_or_create(name=tag_name)
                    tbl_post_tags(post_id=post, tag_id=tag).save()

        # Handle additional images (skip the first since it's featured)
        for i, img_file in enumerate(images[1:]):
            tbl_post_images(post_id=post, image=img_file, order=i).save()

        return redirect('/author/')

    ctx["categories"] = tbl_categories.objects.all()
    return render(request, "author/create.html", ctx)


# ─── 6.2.4 DRAFT & EDIT MODULE ───────────────────────────────────────────────

def drafts(request):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "drafts"})
    if author:
        ctx["drafts"] = tbl_posts.objects.filter(author_id=author, status=False, is_submitted=False).order_by("-id")
    return render(request, "author/drafts.html", ctx)


def edit_post(request, post_id):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "edit"})

    try:
        post = tbl_posts.objects.get(id=post_id, author_id=author)
    except tbl_posts.DoesNotExist:
        return redirect('/author/')

    if request.method == "POST":
        post.title = request.POST.get("title", "").strip()
        post.content = request.POST.get("content", "").strip()
        cat_id = request.POST.get("category")
        status_val = request.POST.get("status", "draft")

        try:
            post.category_id = tbl_categories.objects.get(id=cat_id)
        except tbl_categories.DoesNotExist:
            pass

        post.status = False  # Always False until Admin approves
        post.is_submitted = (status_val == "publish")

        # Auto-generate excerpt from content
        import re
        plain_text = re.sub(r'<[^>]+>', '', post.content).strip()
        post.excerpt = plain_text[:200] + "..." if len(plain_text) > 200 else plain_text

        # Handle images: first new image replaces featured, rest are additional
        images = request.FILES.getlist("images")
        if images:
            post.featured_image = images[0]

        post.save()

        # Handle tags update
        tags_str = request.POST.get("tags", "")
        tbl_post_tags.objects.filter(post_id=post).delete()
        if tags_str:
            for tag_name in tags_str.split(","):
                tag_name = tag_name.strip()
                if tag_name:
                    tag, _ = tbl_tags.objects.get_or_create(name=tag_name)
                    tbl_post_tags(post_id=post, tag_id=tag).save()

        # Handle additional images (skip first since it's featured)
        if len(images) > 1:
            max_order = tbl_post_images.objects.filter(post_id=post).count()
            for i, img_file in enumerate(images[1:]):
                tbl_post_images(post_id=post, image=img_file, order=max_order + i).save()

        return redirect('/author/posts/')

    ctx["post"] = post
    ctx["categories"] = tbl_categories.objects.all()
    ctx["post_tags"] = ", ".join(
        tbl_post_tags.objects.filter(post_id=post).values_list("tag_id__name", flat=True)
    )
    ctx["post_images"] = tbl_post_images.objects.filter(post_id=post).order_by("order")
    return render(request, "author/edit.html", ctx)


# ─── 6.2.5 POST SUBMISSION MODULE ────────────────────────────────────────────

def my_posts(request):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "posts"})
    if author:
        posts = tbl_posts.objects.filter(author_id=author).order_by("-id")
        for post in posts:
            post.like_count = tbl_likes.objects.filter(post_id=post).count()
            post.view_count = tbl_post_views.objects.filter(post_id=post).count()
            post.comment_count = tbl_comments.objects.filter(post_id=post).count()
        ctx["posts"] = posts
    return render(request, "author/posts.html", ctx)


def post_status(request):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "status"})
    if author:
        # Show all posts that are pending approval OR got rejected (maybe we don't have reject yet).
        # We will show posts that are currently 'is_submitted=True' and 'status=False'.
        ctx["pending_posts"] = tbl_posts.objects.filter(author_id=author, is_submitted=True, status=False).order_by("-id")
    return render(request, "author/status.html", ctx)


def publish_draft(request, post_id):
    """Submit a draft post for admin review."""
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    if request.method == "POST":
        try:
            post = tbl_posts.objects.get(id=post_id, author_id=author)
            post.is_submitted = True
            post.status = False  # Ensure it goes to pending, not published
            post.save()
        except tbl_posts.DoesNotExist:
            pass
    return redirect('/author/status/')


def delete_post(request, post_id):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    if request.method == "POST":
        try:
            post = tbl_posts.objects.get(id=post_id, author_id=author)
            post.delete()
        except tbl_posts.DoesNotExist:
            pass
    return redirect('/author/')


def delete_post_image(request, image_id):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    if request.method == "POST":
        try:
            img = tbl_post_images.objects.get(id=image_id, post_id__author_id=author)
            post_id = img.post_id.id
            img.delete()
            return redirect(f'/author/edit/{post_id}/')
        except tbl_post_images.DoesNotExist:
            pass
    return redirect('/author/')


# ─── 6.2.6 MEDIA UPLOAD MODULE ───────────────────────────────────────────────

def media_upload(request):
    guard = require_author(request)
    if guard:
        return guard
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "media"})

    if request.method == "POST":
        file = request.FILES.get("media_file")
        if file:
            user = tbl_user.objects.get(id=request.session['user_id'])
            tbl_media(file_path=file, uploaded_by=user).save()
        return redirect('/author/media/')

    ctx["media_files"] = tbl_media.objects.filter(
        uploaded_by__id=request.session.get('user_id')
    ).order_by("-id") if request.session.get('user_id') else []
    return render(request, "author/media.html", ctx)


# ─── 6.2.7 COMMENT RESPONSE MODULE ──────────────────────────────────────────

def comments(request):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "comments"})
    if author:
        author_posts = tbl_posts.objects.filter(author_id=author)
        ctx["comments"] = tbl_comments.objects.filter(post_id__in=author_posts).order_by("-id")
    return render(request, "author/comments.html", ctx)


def reply_comment(request, comment_id):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    if request.method == "POST" and author:
        reply_text = request.POST.get("reply_text", "").strip()
        if reply_text:
            try:
                comment = tbl_comments.objects.get(id=comment_id, post_id__author_id=author)
                # Create a reply as a comment from the author
                user = tbl_user.objects.get(id=request.session['user_id'])
                tbl_comments(
                    post_id=comment.post_id,
                    user_id=user,
                    comment_text=f"[Author Reply] {reply_text}",
                    parent_id=comment
                ).save()
                # Notify the original commenter
                tbl_notifications(
                    user_id=comment.user_id,
                    title="Author replied to your comment",
                    message=f"{author.user_id.name} replied to your comment on '{comment.post_id.title}'",
                    notification_type='comment',
                    link=f'/reader/blog/{comment.post_id.id}/'
                ).save()
            except tbl_comments.DoesNotExist:
                pass
    return redirect('/author/comments/')


# ─── AUTHOR PROFILE ──────────────────────────────────────────────────────────

def author_profile(request):
    guard = require_author(request)
    if guard:
        return guard
    author = get_author(request)
    ctx = get_session_context(request)
    ctx.update({"zone": "author", "page": "profile"})

    if request.method == "POST" and author:
        author.bio = request.POST.get("bio", "").strip()
        website = request.POST.get("website", "").strip()
        if website:
            author.website = website
        profile_image = request.FILES.get("profile_image")
        if profile_image:
            author.profile_image = profile_image
        author.save()

        # Update user name if changed
        new_name = request.POST.get("name", "").strip()
        if new_name and new_name != author.user_id.name:
            author.user_id.name = new_name
            author.user_id.save()
            request.session['user_name'] = new_name

        ctx['success'] = "Profile updated successfully!"

    if author:
        ctx['author'] = author
        ctx['user_obj'] = author.user_id
    return render(request, "author/profile.html", ctx)

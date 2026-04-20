from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from author.models import tbl_posts, tbl_categories, tbl_post_tags, tbl_post_images, tbl_authors
from .models import tbl_comments, tbl_likes, tbl_bookmarks, tbl_post_views, tbl_readers, tbl_shares, tbl_follows
from accounts.models import tbl_user, tbl_notifications


def get_session_context(request):
    uid = request.session.get('user_id')
    notif_count = 0
    if uid:
        notif_count = tbl_notifications.objects.filter(user_id__id=uid, is_read=False).count()
    return {
        'user_id': uid,
        'user_name': request.session.get('user_name', 'Guest'),
        'user_role': request.session.get('user_role', 'reader'),
        'user_username': request.session.get('user_username', ''),
        'notif_count': notif_count,
    }


# ─── 6.3.2 READER DASHBOARD ─────────────────────────────────────────────────

def dashboard(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "dashboard"})
    uid = request.session.get('user_id')
    ctx["recent_posts"] = tbl_posts.objects.filter(status=True).order_by("-id")[:6]
    ctx["categories"] = tbl_categories.objects.all()

    # Add like/comment counts to posts
    for post in ctx["recent_posts"]:
        post.like_count = tbl_likes.objects.filter(post_id=post).count()
        post.comment_count = tbl_comments.objects.filter(post_id=post).count()
        post.view_count = tbl_post_views.objects.filter(post_id=post).count()

    if uid:
        ctx["liked_count"] = tbl_likes.objects.filter(user_id__id=uid).count()
        ctx["bookmarks_count"] = tbl_bookmarks.objects.filter(user_id__id=uid).count()
        ctx["comments_count"] = tbl_comments.objects.filter(user_id__id=uid).count()
        ctx["views_count"] = tbl_post_views.objects.filter(user_id__id=uid).count()

        # 6.3.2 - Followed authors
        followed_user_ids = tbl_follows.objects.filter(follower_id__id=uid).values_list('following_id', flat=True)
        followed_authors = tbl_authors.objects.filter(user_id__id__in=followed_user_ids)
        ctx["followed_authors"] = followed_authors
        ctx["followed_count"] = followed_authors.count()

        # Posts from followed authors
        if followed_authors.exists():
            followed_posts = tbl_posts.objects.filter(
                author_id__in=followed_authors, status=True
            ).order_by("-id")[:6]
            for post in followed_posts:
                post.like_count = tbl_likes.objects.filter(post_id=post).count()
                post.comment_count = tbl_comments.objects.filter(post_id=post).count()
            ctx["followed_posts"] = followed_posts
    return render(request, "reader/dashboard.html", ctx)


# ─── 6.3.3 CONTENT BROWSING MODULE ──────────────────────────────────────────

def browse(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "browse"})
    posts = tbl_posts.objects.filter(status=True).order_by("-id")

    # Search
    q = request.GET.get("q", "").strip()
    if q:
        from django.db.models import Q
        posts = posts.filter(
            Q(title__icontains=q) | Q(content__icontains=q) |
            Q(author_id__user_id__name__icontains=q) | Q(category_id__name__icontains=q)
        )
        ctx["people_results"] = tbl_user.objects.filter(
            Q(username__icontains=q) | Q(name__icontains=q)
        ).order_by("-id")[:10]

    # Category filter
    cat = request.GET.get("category", "")
    if cat:
        posts = posts.filter(category_id__id=cat)

    # Tag filter
    tag = request.GET.get("tag", "")
    if tag:
        post_ids = tbl_post_tags.objects.filter(tag_id__name=tag).values_list('post_id', flat=True)
        posts = posts.filter(id__in=post_ids)

    # Add counts to posts
    for post in posts:
        post.like_count = tbl_likes.objects.filter(post_id=post).count()
        post.comment_count = tbl_comments.objects.filter(post_id=post).count()
        post.view_count = tbl_post_views.objects.filter(post_id=post).count()

    ctx["posts"] = posts
    ctx["categories"] = tbl_categories.objects.all()
    ctx["search_query"] = q
    ctx["selected_category"] = cat
    ctx["selected_tag"] = tag
    return render(request, "reader/browse.html", ctx)


# ─── 6.3.4 BLOG VIEW MODULE ─────────────────────────────────────────────────

def blog_view(request, post_id):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "blog"})
    post = get_object_or_404(tbl_posts, id=post_id, status=True)
    ctx["post"] = post
    ctx["post_tags"] = tbl_post_tags.objects.filter(post_id=post)
    ctx["post_images"] = tbl_post_images.objects.filter(post_id=post).order_by('order')
    ctx["comments"] = tbl_comments.objects.filter(post_id=post, parent_id__isnull=True).order_by("-id")
    ctx["comment_count"] = tbl_comments.objects.filter(post_id=post).count()
    ctx["like_count"] = tbl_likes.objects.filter(post_id=post).count()
    ctx["view_count"] = tbl_post_views.objects.filter(post_id=post).count()
    ctx["share_count"] = tbl_shares.objects.filter(post_id=post).count()

    # Related posts
    ctx["related_posts"] = tbl_posts.objects.filter(
        category_id=post.category_id, status=True
    ).exclude(id=post.id).order_by("-id")[:3]

    uid = request.session.get('user_id')
    if uid:
        try:
            user = tbl_user.objects.get(id=uid)
            ctx["user_liked"] = tbl_likes.objects.filter(post_id=post, user_id=user).exists()
            ctx["user_bookmarked"] = tbl_bookmarks.objects.filter(post_id=post, user_id=user).exists()
        except tbl_user.DoesNotExist:
            pass

        # Track view (once per user per post)
        try:
            user = tbl_user.objects.get(id=uid)
            if not tbl_post_views.objects.filter(post_id=post, user_id=user).exists():
                tbl_post_views(post_id=post, user_id=user).save()
        except tbl_user.DoesNotExist:
            pass

    # Handle comment POST (6.3.5)
    if request.method == "POST" and uid:
        action = request.POST.get("action", "comment")
        if action == "comment":
            text = request.POST.get("comment_text", "").strip()
            if text:
                user = tbl_user.objects.get(id=uid)
                parent_comment_id = request.POST.get("parent_id")
                parent = None
                if parent_comment_id:
                    try:
                        parent = tbl_comments.objects.get(id=parent_comment_id)
                    except tbl_comments.DoesNotExist:
                        pass
                tbl_comments(post_id=post, user_id=user, comment_text=text, parent_id=parent).save()
                # Notify author
                if post.author_id.user_id.id != user.id:
                    tbl_notifications(
                        user_id=post.author_id.user_id,
                        title="New comment on your post",
                        message=f"{user.name} commented on '{post.title}'",
                        notification_type='comment',
                        link=f'/reader/blog/{post_id}/'
                    ).save()
                return redirect(f'/reader/blog/{post_id}/')

    return render(request, "reader/blog.html", ctx)


# ─── 6.3.6 LIKE / SHARE MODULE ──────────────────────────────────────────────

@require_POST
def ajax_like(request, post_id):
    uid = request.session.get('user_id')
    if not uid:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        user = tbl_user.objects.get(id=uid)
        post = get_object_or_404(tbl_posts, id=post_id)
        like_exists = tbl_likes.objects.filter(post_id=post, user_id=user)
        if like_exists.exists():
            like_exists.delete()
            liked = False
        else:
            tbl_likes(post_id=post, user_id=user).save()
            liked = True
            if post.author_id.user_id.id != user.id:
                tbl_notifications(
                    user_id=post.author_id.user_id,
                    title="Someone liked your post",
                    message=f"{user.name} liked '{post.title}'",
                    notification_type='like',
                    link=f'/reader/blog/{post.id}/'
                ).save()
        count = tbl_likes.objects.filter(post_id=post).count()
        return JsonResponse({'liked': liked, 'count': count})
    except tbl_user.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@require_POST
def ajax_bookmark(request, post_id):
    uid = request.session.get('user_id')
    if not uid:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        user = tbl_user.objects.get(id=uid)
        post = get_object_or_404(tbl_posts, id=post_id)
        bm_exists = tbl_bookmarks.objects.filter(post_id=post, user_id=user)
        if bm_exists.exists():
            bm_exists.delete()
            bookmarked = False
        else:
            tbl_bookmarks(post_id=post, user_id=user).save()
            bookmarked = True
        return JsonResponse({'bookmarked': bookmarked})
    except tbl_user.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


@require_POST
def ajax_share(request, post_id):
    uid = request.session.get('user_id')
    if not uid:
        return JsonResponse({'error': 'Login required'}, status=401)
    try:
        user = tbl_user.objects.get(id=uid)
        post = get_object_or_404(tbl_posts, id=post_id)
        platform = request.POST.get('platform', 'link')
        tbl_shares(post_id=post, user_id=user, platform=platform).save()
        count = tbl_shares.objects.filter(post_id=post).count()
        return JsonResponse({'shared': True, 'count': count})
    except tbl_user.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


# ─── 6.3.7 NOTIFICATION MODULE ──────────────────────────────────────────────

def notifications(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "notifications"})
    uid = request.session.get('user_id')
    if uid:
        ctx["notifications"] = tbl_notifications.objects.filter(user_id__id=uid).order_by("-id")
    return render(request, "reader/notifications.html", ctx)


def mark_notification_read(request, notif_id):
    uid = request.session.get('user_id')
    if uid:
        try:
            notif = tbl_notifications.objects.get(id=notif_id, user_id__id=uid)
            notif.is_read = True
            notif.save()
            if notif.link:
                return redirect(notif.link)
        except tbl_notifications.DoesNotExist:
            pass
    return redirect('/reader/notifications/')


def mark_all_read(request):
    uid = request.session.get('user_id')
    if uid and request.method == "POST":
        tbl_notifications.objects.filter(user_id__id=uid, is_read=False).update(is_read=True)
    return redirect('/reader/notifications/')


# ─── BOOKMARKS & HISTORY ────────────────────────────────────────────────────

def bookmarks(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "bookmarks"})
    uid = request.session.get('user_id')
    if uid:
        ctx["bookmarks"] = tbl_bookmarks.objects.filter(user_id__id=uid).order_by("-id")
    return render(request, "reader/bookmarks.html", ctx)


def history(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "history"})
    uid = request.session.get('user_id')
    if uid:
        ctx["history"] = tbl_post_views.objects.filter(user_id__id=uid).order_by("-id")
    return render(request, "reader/history.html", ctx)


# ─── PROFILE ─────────────────────────────────────────────────────────────────

def profile(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "profile"})
    uid = request.session.get('user_id')
    if uid:
        try:
            user = tbl_user.objects.get(id=uid)
            ctx["profile_user"] = user
            ctx["is_author"] = tbl_authors.objects.filter(user_id=user).exists()
            ctx["liked_count"] = tbl_likes.objects.filter(user_id__id=uid).count()
            ctx["bookmarks_count"] = tbl_bookmarks.objects.filter(user_id__id=uid).count()

            if request.method == "POST":
                new_name = request.POST.get("name", "").strip()
                if new_name:
                    user.name = new_name
                    user.save()
                    request.session['user_name'] = new_name

                # Update reader profile image
                try:
                    reader = tbl_readers.objects.get(user_id=user)
                    profile_image = request.FILES.get("profile_image")
                    if profile_image:
                        reader.profile_image = profile_image
                        reader.save()
                    bio = request.POST.get("bio", "").strip()
                    if bio:
                        reader.bio = bio
                        reader.save()
                except tbl_readers.DoesNotExist:
                    pass
                ctx['success'] = "Profile updated!"

        except tbl_user.DoesNotExist:
            pass
    return render(request, "reader/profile.html", ctx)


def upgrade_to_author(request):
    uid = request.session.get('user_id')
    if not uid:
        return redirect('/accounts/login/')
    if request.method == "POST":
        bio = request.POST.get("bio", "").strip()
        try:
            user = tbl_user.objects.get(id=uid)
            user.role = 'author'
            user.save()
            if not tbl_authors.objects.filter(user_id=user).exists():
                tbl_authors(user_id=user, bio=bio or f"Hi, I'm {user.name}!").save()
            request.session['user_role'] = 'author'
            return redirect('/author/')
        except tbl_user.DoesNotExist:
            pass
    return redirect('/reader/profile/')


def public_profile(request, username):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "public_profile"})
    try:
        target_user = tbl_user.objects.get(username=username)
        ctx["target_user"] = target_user
        # Follower / Following counts
        ctx["follower_count"] = tbl_follows.objects.filter(following_id=target_user).count()
        ctx["following_count"] = tbl_follows.objects.filter(follower_id=target_user).count()
        uid = request.session.get('user_id')
        if uid and uid != target_user.id:
            ctx["is_following"] = tbl_follows.objects.filter(
                follower_id__id=uid, following_id=target_user
            ).exists()
        try:
            author = tbl_authors.objects.get(user_id=target_user)
            user_posts = tbl_posts.objects.filter(author_id=author, status=True).order_by("-id")
            for post in user_posts:
                post.like_count = tbl_likes.objects.filter(post_id=post).count()
                post.view_count = tbl_post_views.objects.filter(post_id=post).count()
            ctx["user_posts"] = user_posts
            ctx["post_count"] = user_posts.count()
            ctx["author_bio"] = author.bio
            ctx["author_profile"] = author
        except tbl_authors.DoesNotExist:
            ctx["user_posts"] = []
            ctx["post_count"] = 0
        ctx["total_views"] = tbl_post_views.objects.filter(
            post_id__author_id__user_id=target_user
        ).count()
    except tbl_user.DoesNotExist:
        ctx["target_user"] = None
    return render(request, "reader/public_profile.html", ctx)


# ─── FOLLOW / UNFOLLOW ──────────────────────────────────────────────────────

@require_POST
def ajax_follow(request, user_id):
    """Toggle follow/unfollow a user."""
    uid = request.session.get('user_id')
    if not uid:
        return JsonResponse({'error': 'Login required'}, status=401)
    if uid == user_id:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    try:
        follower = tbl_user.objects.get(id=uid)
        target = tbl_user.objects.get(id=user_id)
        follow_exists = tbl_follows.objects.filter(follower_id=follower, following_id=target)
        if follow_exists.exists():
            follow_exists.delete()
            following = False
        else:
            tbl_follows(follower_id=follower, following_id=target).save()
            following = True
            # Notify the target user
            tbl_notifications(
                user_id=target,
                title="New Follower!",
                message=f"{follower.name} started following you.",
                notification_type='follow',
                link=f'/reader/user/{follower.username}/'
            ).save()
        count = tbl_follows.objects.filter(following_id=target).count()
        return JsonResponse({'following': following, 'count': count})
    except tbl_user.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)


# ─── LIKED POSTS PAGE ────────────────────────────────────────────────────────
def liked_posts(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "reader", "page": "liked_posts"})
    uid = request.session.get('user_id')
    if uid:
        ctx["liked_posts"] = tbl_likes.objects.filter(user_id__id=uid).order_by("-id")
    return render(request, "reader/liked_posts.html", ctx)

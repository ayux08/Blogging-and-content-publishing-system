from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import tbl_user, tbl_contact, tbl_notifications
from author.models import tbl_posts, tbl_categories, tbl_authors, tbl_media, tbl_tags
from reader.models import tbl_comments, tbl_likes, tbl_bookmarks, tbl_post_views, tbl_readers, tbl_shares
import re


# ─── HELPER FUNCTIONS ────────────────────────────────────────────────────────

def get_session_context(request):
    """Returns common session data for templates."""
    uid = request.session.get('user_id')
    notif_count = 0
    if uid:
        notif_count = tbl_notifications.objects.filter(user_id__id=uid, is_read=False).count()
    return {
        'user_id': uid,
        'user_name': request.session.get('user_name', 'Guest'),
        'user_email': request.session.get('user_email', ''),
        'user_role': request.session.get('user_role', 'reader'),
        'user_username': request.session.get('user_username', ''),
        'notif_count': notif_count,
    }


def require_login(request):
    """Returns redirect if user is not logged in, else None."""
    if not request.session.get('user_id'):
        return redirect('/accounts/login/')
    return None


def require_role(request, allowed_roles):
    """Returns redirect if user doesn't have correct role, else None."""
    check = require_login(request)
    if check:
        return check
    user_role = request.session.get('user_role', 'reader').lower()
    if user_role not in allowed_roles:
        if user_role == 'admin':
            return redirect('/admin_zone/')
        elif user_role == 'author':
            return redirect('/author/')
        else:
            return redirect('/reader/')
    return None


# ─── PORTAL / LANDING PAGE ───────────────────────────────────────────────────

def portal(request):
    """Landing page - redirects logged-in users to their zone."""
    if request.session.get('user_id'):
        role = request.session.get('user_role', 'reader').lower()
        if role == 'admin':
            return redirect('/admin_zone/')
        elif role == 'author':
            return redirect('/author/')
        else:
            return redirect('/reader/')
    # Show featured posts on landing page
    ctx = {
        'featured_posts': tbl_posts.objects.filter(status=True).order_by('-id')[:6],
        'total_posts': tbl_posts.objects.filter(status=True).count(),
        'total_authors': tbl_authors.objects.count(),
        'total_readers': tbl_readers.objects.count(),
        'categories': tbl_categories.objects.all()[:8],
    }
    return render(request, "portal.html", ctx)


# ─── AUTHENTICATION VIEWS ────────────────────────────────────────────────────

def login_view(request):
    """6.2.1 / 6.3.1 - Login for authors and readers."""
    if request.session.get('user_id'):
        role = request.session.get('user_role', 'reader').lower()
        if role == 'admin':
            return redirect('/admin_zone/')
        elif role == 'author':
            return redirect('/author/')
        else:
            return redirect('/reader/')

    if request.method == "POST":
        login_id = request.POST.get("login_id", "").strip()
        password = request.POST.get("password", "").strip()

        from django.db.models import Q
        user = None

        try:
            user = tbl_user.objects.get(Q(email=login_id) | Q(username=login_id), password=password)
        except tbl_user.DoesNotExist:
            pass

        # Fallback for Django superuser (e.g. from python manage.py createsuperuser)
        if not user:
            from django.contrib.auth.models import User
            try:
                # Try getting the Django user by username or email
                django_user = User.objects.filter(Q(username=login_id) | Q(email=login_id)).first()
                if django_user and django_user.check_password(password) and django_user.is_superuser:
                    # Sync this superuser into our custom tbl_user table
                    user, created = tbl_user.objects.get_or_create(
                        username=django_user.username,
                        defaults={
                            'name': django_user.first_name or 'Admin',
                            'email': django_user.email or f"{django_user.username}@admin.com",
                            'password': password,
                            'role': 'admin',
                            'status': True
                        }
                    )
                    if not created:
                        # Update password to match in case they changed it via Django auth
                        user.password = password
                        user.role = 'admin'
                        user.save()
            except Exception:
                pass

        if not user:
            return render(request, "accounts/login.html", {"error": "Invalid username/email or password."})

        if not user.status:
            return render(request, "accounts/login.html", {"error": "Your account has been deactivated. Contact admin."})

        # Store user info in session
        request.session['user_id'] = user.id
        request.session['user_name'] = user.name
        request.session['user_email'] = user.email
        request.session['user_role'] = user.role or 'reader'
        request.session['user_username'] = user.username or ''
        
        # Redirect based on role
        user_role = (user.role or 'reader').lower()
        if user_role == 'admin':
            return redirect('/admin_zone/')
        elif user_role == 'author':
            return redirect('/author/')
        else:
            return redirect('/reader/')

    return render(request, "accounts/login.html")


def register_view(request):
    """6.2.1 / 6.3.1 - Registration for authors and readers."""
    if request.session.get('user_id'):
        return redirect('/reader/')

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        username = request.POST.get("username", "").strip().lower()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        role = request.POST.get("role", "reader").strip().lower()

        # Validate
        if not re.match(r'^[a-z0-9_]{3,30}$', username):
            return render(request, "accounts/register.html",
                          {"error": "Username must be 3-30 characters: lowercase letters, numbers, underscores only."})
        if tbl_user.objects.filter(username=username).exists():
            return render(request, "accounts/register.html", {"error": "Username already taken."})
        if tbl_user.objects.filter(email=email).exists():
            return render(request, "accounts/register.html", {"error": "Email already registered."})
        if len(password) < 4:
            return render(request, "accounts/register.html", {"error": "Password must be at least 4 characters."})

        # Create user
        if role not in ['author', 'reader']:
            role = 'reader'

        user = tbl_user(name=name, username=username, email=email, password=password, role=role, status=True)
        user.save()

        # Create profile based on role
        if role == 'author':
            bio = request.POST.get("bio", "").strip()
            tbl_authors(user_id=user, bio=bio or f"Hi, I'm {name}!").save()
        else:
            tbl_readers(user_id=user).save()

        # Auto-login
        request.session['user_id'] = user.id
        request.session['user_name'] = user.name
        request.session['user_email'] = user.email
        request.session['user_role'] = role
        request.session['user_username'] = user.username

        # Welcome notification
        tbl_notifications(user_id=user, title="Welcome to Blogverse!",
                          message=f"Welcome {name}! Start exploring amazing content on Blogverse.",
                          notification_type='system').save()

        if role == 'author':
            return redirect('/author/')
        return redirect('/reader/')
    return render(request, "accounts/register.html")


def logout_view(request):
    """Logout and clear session."""
    request.session.flush()
    return redirect('/')


def contact_view(request):
    """Contact form."""
    ctx = get_session_context(request)
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        mobile = request.POST.get("mobile", "").strip()
        message = request.POST.get("message", "").strip()
        tbl_contact(name=name, email=email, mobile=mobile, message=message).save()
        ctx['success'] = "Your message has been sent successfully!"
    return render(request, "accounts/contact.html", ctx)


# ─── ADMIN ZONE VIEWS ────────────────────────────────────────────────────────

def admin_dashboard(request):
    """6.1.1 Admin Login + 6.1.2 Admin Dashboard Module."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    ctx = get_session_context(request)

    # Top categories with post counts
    top_categories = []
    for cat in tbl_categories.objects.all():
        count = tbl_posts.objects.filter(category_id=cat, status=True).count()
        if count > 0:
            top_categories.append({'category': cat, 'post_count': count})
    top_categories.sort(key=lambda x: x['post_count'], reverse=True)

    ctx.update({
        "zone": "admin", "page": "dashboard",
        "total_users": tbl_user.objects.count(),
        "total_authors": tbl_user.objects.filter(role='author').count(),
        "total_readers": tbl_user.objects.filter(role='reader').count(),
        "total_posts": tbl_posts.objects.count(),
        "published_posts": tbl_posts.objects.filter(status=True).count(),
        "live_posts": tbl_posts.objects.filter(status=True).count(),
        "draft_posts": tbl_posts.objects.filter(status=False).count(),
        "total_categories": tbl_categories.objects.count(),
        "total_comments": tbl_comments.objects.count(),
        "total_likes": tbl_likes.objects.count(),
        "total_views": tbl_post_views.objects.count(),
        "pending_posts": tbl_posts.objects.filter(status=False).count(),
        "recent_posts": tbl_posts.objects.order_by("-id")[:5],
        "recent_users": tbl_user.objects.order_by("-id")[:5],
        "recent_comments": tbl_comments.objects.order_by("-id")[:5],
        "top_categories": top_categories[:6],
    })
    return render(request, "admin_zone/dashboard.html", ctx)


def admin_users(request):
    """6.1.3 User Management Module - manage author & reader accounts."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    ctx = get_session_context(request)

    # Filter by role
    role_filter = request.GET.get('role', '')
    users = tbl_user.objects.all().order_by("-id")
    if role_filter:
        users = users.filter(role=role_filter)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q
        users = users.filter(Q(name__icontains=q) | Q(username__icontains=q) | Q(email__icontains=q))

    ctx.update({
        "zone": "admin", "page": "users",
        "users": users,
        "role_filter": role_filter,
        "search_query": q,
    })
    return render(request, "admin_zone/users.html", ctx)


def admin_toggle_user(request, user_id):
    """6.1.3 - Activate/deactivate user accounts."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    if request.method == "POST":
        try:
            user = tbl_user.objects.get(id=user_id)
            user.status = not user.status
            user.save()
        except tbl_user.DoesNotExist:
            pass
    return redirect('/admin_zone/users/')


def admin_delete_user(request, user_id):
    """6.1.3 - Delete user account."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    if request.method == "POST":
        try:
            user = tbl_user.objects.get(id=user_id)
            if user.role != 'admin':  # Don't delete admins
                user.delete()
        except tbl_user.DoesNotExist:
            pass
    return redirect('/admin_zone/users/')


def admin_categories(request):
    """6.1.4 Content Category Management Module."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard

    if request.method == "POST":
        action = request.POST.get("action", "add")
        if action == "add":
            name = request.POST.get("category_name", "").strip()
            description = request.POST.get("category_description", "").strip()
            if name and not tbl_categories.objects.filter(name=name).exists():
                tbl_categories(name=name, description=description).save()
        elif action == "edit":
            cat_id = request.POST.get("category_id")
            new_name = request.POST.get("category_name", "").strip()
            description = request.POST.get("category_description", "").strip()
            if cat_id and new_name:
                try:
                    cat = tbl_categories.objects.get(id=cat_id)
                    cat.name = new_name
                    cat.description = description
                    cat.save()
                except tbl_categories.DoesNotExist:
                    pass
        return redirect('/admin_zone/categories/')

    ctx = get_session_context(request)
    categories = tbl_categories.objects.all().order_by("name")
    # Add post count and slug for each category
    for cat in categories:
        cat.post_count = tbl_posts.objects.filter(category_id=cat).count()
        cat.slug = cat.name.lower().replace(' ', '-').replace('&', '').replace('  ', ' ').strip('-')
    ctx.update({
        "zone": "admin", "page": "categories",
        "categories": categories,
    })
    return render(request, "admin_zone/categories.html", ctx)


def admin_delete_category(request, cat_id):
    """6.1.4 - Delete a category."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    if request.method == "POST":
        try:
            tbl_categories.objects.get(id=cat_id).delete()
        except tbl_categories.DoesNotExist:
            pass
    return redirect('/admin_zone/categories/')


def admin_posts(request):
    """6.1.5 Post Approval & Moderation Module."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard

    if request.method == "POST":
        post_id = request.POST.get("post_id")
        action = request.POST.get("action")
        try:
            post = tbl_posts.objects.get(id=post_id)
            if action == "approve":
                post.status = True
                post.save()
                # Notify author
                tbl_notifications(user_id=post.author_id.user_id,
                                  title="Post Approved!",
                                  message=f"Your post '{post.title}' has been approved and is now published.",
                                  notification_type='system',
                                  link=f'/reader/blog/{post.id}/').save()
                # Notify all followers of this author
                from reader.models import tbl_follows
                followers = tbl_follows.objects.filter(following_id=post.author_id.user_id)
                for follow in followers:
                    tbl_notifications(
                        user_id=follow.follower_id,
                        title="New Post from " + post.author_id.user_id.name,
                        message=f"{post.author_id.user_id.name} published a new post: '{post.title}'",
                        notification_type='post',
                        link=f'/reader/blog/{post.id}/'
                    ).save()
            elif action == "reject":
                # Notify author before deleting
                tbl_notifications(user_id=post.author_id.user_id,
                                  title="Post Rejected",
                                  message=f"Your post '{post.title}' has been rejected by admin.",
                                  notification_type='system').save()
                post.delete()
            elif action == "unpublish":
                post.status = False
                post.save()
        except tbl_posts.DoesNotExist:
            pass
        return redirect('/admin_zone/posts/')

    ctx = get_session_context(request)
    # Filter
    status_filter = request.GET.get('status', '')
    # Only show posts that authors have actually submitted
    posts = tbl_posts.objects.filter(is_submitted=True).order_by("-id")
    if status_filter == 'published':
        posts = posts.filter(status=True)
    elif status_filter == 'pending':
        posts = posts.filter(status=False)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q
        posts = posts.filter(Q(title__icontains=q) | Q(author_id__user_id__username__icontains=q))

    # Add views count for each post
    for post in posts:
        post.views_count = tbl_post_views.objects.filter(post_id=post).count()

    ctx.update({
        "zone": "admin", "page": "posts",
        "posts": posts,
        "status_filter": status_filter,
        "search_query": q,
    })
    return render(request, "admin_zone/posts.html", ctx)


def admin_comments(request):
    """6.1.6 Comment Moderation Module."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard

    if request.method == "POST":
        comment_id = request.POST.get("comment_id")
        action = request.POST.get("action")
        try:
            comment = tbl_comments.objects.get(id=comment_id)
            if action == "approve":
                comment.status = True
                comment.save()
            elif action == "reject":
                comment.status = False
                comment.save()
            elif action == "delete":
                comment.delete()
        except tbl_comments.DoesNotExist:
            pass
        return redirect('/admin_zone/comments/')

    ctx = get_session_context(request)
    comments = tbl_comments.objects.all().order_by("-id")

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter == 'approved':
        comments = comments.filter(status=True)
    elif status_filter == 'rejected':
        comments = comments.filter(status=False)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        from django.db.models import Q
        comments = comments.filter(
            Q(comment_text__icontains=q) | Q(user_id__username__icontains=q) | Q(post_id__title__icontains=q)
        )

    ctx.update({
        "zone": "admin", "page": "comments",
        "comments": comments,
        "status_filter": status_filter,
        "search_query": q,
    })
    return render(request, "admin_zone/comments.html", ctx)


def admin_media(request):
    """6.1.7 Media Management Module."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    ctx = get_session_context(request)
    ctx.update({
        "zone": "admin", "page": "media",
        "media_files": tbl_media.objects.all().order_by("-id"),
    })
    return render(request, "admin_zone/media.html", ctx)


def admin_delete_media(request, media_id):
    """6.1.7 - Delete media file."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    if request.method == "POST":
        try:
            tbl_media.objects.get(id=media_id).delete()
        except tbl_media.DoesNotExist:
            pass
    return redirect('/admin_zone/media/')


def admin_analytics(request):
    """6.1.8 Reports & Analytics Module."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    ctx = get_session_context(request)

    # Content performance
    top_posts = tbl_posts.objects.filter(status=True).order_by("-id")[:10]
    post_analytics = []
    for post in top_posts:
        post_analytics.append({
            'post': post,
            'views': tbl_post_views.objects.filter(post_id=post).count(),
            'likes': tbl_likes.objects.filter(post_id=post).count(),
            'comments': tbl_comments.objects.filter(post_id=post).count(),
            'shares': tbl_shares.objects.filter(post_id=post).count(),
        })

    # Category stats
    category_stats = []
    for cat in tbl_categories.objects.all():
        category_stats.append({
            'category': cat,
            'post_count': tbl_posts.objects.filter(category_id=cat, status=True).count(),
        })

    ctx.update({
        "zone": "admin", "page": "analytics",
        "total_users": tbl_user.objects.count(),
        "total_posts": tbl_posts.objects.count(),
        "total_views": tbl_post_views.objects.count(),
        "total_comments": tbl_comments.objects.count(),
        "total_likes": tbl_likes.objects.count(),
        "total_shares": tbl_shares.objects.count(),
        "total_authors": tbl_user.objects.filter(role='author').count(),
        "total_readers": tbl_user.objects.filter(role='reader').count(),
        "post_analytics": post_analytics,
        "category_stats": category_stats,
    })
    return render(request, "admin_zone/analytics.html", ctx)


# ─── 6.1.1 ADMIN LOGIN (unified via accounts/login) ─────────────────────────
# Admin login is now handled by the unified login_view in accounts.
# The separate admin_login view has been removed.


# ─── 6.1.4 TAGS MANAGEMENT ───────────────────────────────────────────────────

def admin_tags(request):
    """6.1.4 - Manage tags alongside categories."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard

    if request.method == "POST":
        action = request.POST.get("action", "add")
        if action == "add":
            name = request.POST.get("tag_name", "").strip()
            if name and not tbl_tags.objects.filter(name=name).exists():
                tbl_tags(name=name).save()
        elif action == "edit":
            tag_id = request.POST.get("tag_id")
            new_name = request.POST.get("tag_name", "").strip()
            if tag_id and new_name:
                try:
                    tag = tbl_tags.objects.get(id=tag_id)
                    tag.name = new_name
                    tag.save()
                except tbl_tags.DoesNotExist:
                    pass
        return redirect('/admin_zone/tags/')

    ctx = get_session_context(request)
    from author.models import tbl_post_tags
    tags = tbl_tags.objects.all().order_by("-id")
    for tag in tags:
        tag.post_count = tbl_post_tags.objects.filter(tag_id=tag).count()
    ctx.update({
        "zone": "admin", "page": "tags",
        "tags": tags,
    })
    return render(request, "admin_zone/tags.html", ctx)


def admin_delete_tag(request, tag_id):
    """6.1.4 - Delete a tag."""
    guard = require_role(request, ['admin'])
    if guard:
        return guard
    if request.method == "POST":
        try:
            tbl_tags.objects.get(id=tag_id).delete()
        except tbl_tags.DoesNotExist:
            pass
    return redirect('/admin_zone/tags/')


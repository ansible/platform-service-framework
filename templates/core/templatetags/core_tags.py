"""Custom template tags for the core app."""

from django import template
from django.conf import settings
from django.utils.html import escape, format_html

register = template.Library()


def _get_full_path(request):
    """Get full path including service prefix.

    The middleware patches get_full_path() to return the prefixed path
    for both access patterns:
    - /api/<service>/...: patched to return /api/<service>/...
    - /<service>/...: patched to return /<service>/...
    """
    return request.get_full_path()


@register.simple_tag
def script_name(request):
    """Return the SCRIPT_NAME (service prefix) or '/' if not set."""
    prefix = request.META.get("SCRIPT_NAME", "") or "/"
    return prefix if prefix.endswith("/") else prefix + "/"


@register.simple_tag
def login_link(request):
    """
    Return a login link using the LOGIN_URL setting.
    Falls back to /api-auth/login/ if LOGIN_URL is not set.
    """
    login_url = getattr(settings, "LOGIN_URL", "/api-auth/login/")
    full_path = _get_full_path(request)
    snippet = "<li><a href='{href}?next={next}'>Log in</a></li>"
    return format_html(snippet, href=login_url, next=escape(full_path))


@register.simple_tag
def logout_link(request, user, csrf_token):
    """
    Return a logout dropdown using the LOGOUT_URL setting.
    Falls back to /api-auth/logout/ if LOGOUT_URL is not set.
    """
    logout_url = getattr(settings, "LOGOUT_URL", "/api-auth/logout/")
    full_path = _get_full_path(request)

    snippet = """<li class="dropdown">
        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
            {user}
            <b class="caret"></b>
        </a>
        <ul class="dropdown-menu">
            <form id="logoutForm" method="post" action="{href}?next={next}">
                <input type="hidden" name="csrfmiddlewaretoken" value="{csrf_token}">
            </form>
            <li>
                <a href="#" onclick='document.getElementById("logoutForm").submit()'>Log out</a>
            </li>
        </ul>
    </li>"""
    return format_html(
        snippet, user=escape(user), href=logout_url, next=escape(full_path), csrf_token=csrf_token
    )

from django import template

from connection.models import Block, Follow, Contact

register = template.Library()


@register.simple_tag(takes_context=True)
def get_by_name(context, name):
    """Tag to lookup a variable in the current context."""
    return context[name]


@register.inclusion_tag("connection/templatetags/connections.html")
def connections(user):
    """
    Simple tag to grab all connections
    """
    return {"connections": Contact.objects.connections(user)}


@register.inclusion_tag("connection/templatetags/followers.html")
def followers(user):
    """
    Simple tag to grab all followers
    """
    return {"followers": Follow.objects.followers(user)}


@register.inclusion_tag("connection/templatetags/following.html")
def following(user):
    """
    Simple tag to grab all users who follow the given user
    """
    return {"following": Follow.objects.following(user)}


@register.inclusion_tag("connection/templatetags/blockers.html")
def blockers(user):
    """
    Simple tag to grab all followers
    """
    return {"blockers": Block.objects.blocked(user)}


@register.inclusion_tag("connection/templatetags/blocking.html")
def blocking(user):
    """
    Simple tag to grab all users who follow the given user
    """
    return {"blocking": Block.objects.blocking(user)}


@register.inclusion_tag("connection/templatetags/connection_requests.html")
def connection_requests(user):
    """
    Inclusion tag to display connection requests
    """
    return {"connection_requests": Contact.objects.requests(user)}


@register.inclusion_tag("connection/templatetags/connection_request_count.html")
def connection_request_count(user):
    """
    Inclusion tag to display the count of unread connection requests
    """
    return {"connection_request_count": Contact.objects.unread_request_count(user)}


@register.inclusion_tag("connection/templatetags/connection_count.html")
def connection_count(user):
    """
    Inclusion tag to display the total count of connections for the given user
    """
    return {"connection_count": len(Contact.objects.connections(user))}


@register.inclusion_tag("connection/templatetags/connection_rejected_count.html")
def connection_rejected_count(user):
    """
    Inclusion tag to display the count of rejected connection requests
    """
    return {"connection_rejected_count": len(Contact.objects.rejected_requests(user))}

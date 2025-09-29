from django import template
from home.models import Notification

register = template.Library()

@register.simple_tag
def get_unread_notification_count(user):
    if user.is_authenticated:
        return Notification.objects.filter(user=user, is_read=False).count()
    return 0

@register.inclusion_tag('notification_dropdown.html')
def notification_dropdown(user):
    if user.is_authenticated:
        notifications = Notification.objects.filter(user=user).order_by('-created_at')[:5]
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
    else:
        notifications = []
        unread_count = 0
    
    return {
        'notifications': notifications,
        'unread_count': unread_count,
        'user': user
    }
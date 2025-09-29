from .models import Notification

def notification_context(request):
    context = {}
    if request.user.is_authenticated:
        try:
            # Unread notifications count
            context['unread_notification_count'] = Notification.objects.filter(
                user=request.user, 
                is_read=False
            ).count()
            
            # Recent notifications (last 5)
            context['recent_notifications'] = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:5]
            
        except Exception as e:
            # Agar koi error aaye to default values set karein
            context['unread_notification_count'] = 0
            context['recent_notifications'] = []
    else:
        context['unread_notification_count'] = 0
        context['recent_notifications'] = []
    
    return context
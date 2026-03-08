from .models import Notification

def notification_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'unread_notifications': notifications,
            'unread_count': unread_count
        }
    return {}

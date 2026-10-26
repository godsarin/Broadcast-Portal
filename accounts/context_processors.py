from .models import Notification


def notifications_processor(request):
    """Makes notifications available on every page automatically"""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )[:10]
        notification_count = notifications.count()
        return {
            'notifications': notifications,
            'notification_count': notification_count,
        }
    return {
        'notifications': [],
        'notification_count': 0,
    }
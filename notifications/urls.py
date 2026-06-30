from django.urls import path
from .views import MarkNotificationReadView, MarkAllNotificationsReadView

app_name = 'notifications'

urlpatterns = [
    path('read/<int:pk>/', MarkNotificationReadView.as_view(), name='mark_read'),
    path('read/all/', MarkAllNotificationsReadView.as_view(), name='mark_all_read'),
]

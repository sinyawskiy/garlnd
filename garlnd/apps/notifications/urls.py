from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.notifications.views import NotificationsListView


urlpatterns = [
    path('rules/<rule_id>/notifications/', login_required(NotificationsListView.as_view()), name='notifications_list')
]

from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from apps.account.views import MainPageView, FeedbackView

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('account/', login_required(TemplateView.as_view(template_name='account.html')), name='account'),
    path('agreement/', TemplateView.as_view(template_name='agreement.html'), name='agreement'),
    path('api/', TemplateView.as_view(template_name='api.html'), name='api'),
    path('donate/', TemplateView.as_view(template_name='donate.html'), name='donate'),
    path('feedback/', FeedbackView.as_view(), name='feedback')
]
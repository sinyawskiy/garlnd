from django.urls import path
from django.contrib.auth.decorators import login_required
from apps.rules.views import RulesListView, RuleEditView, RuleAddView, RuleDeleteView, RuleActivateView

urlpatterns = [
    path('', login_required(RulesListView.as_view()), name='rules_list'),
    path('add/', login_required(RuleAddView.as_view()), name='add_rule'),
    path('edit/<rule_id>/', login_required(RuleEditView.as_view()), name='edit_rule'),
    path('delete/<pk>/', login_required(RuleDeleteView.as_view()), name='delete_rule'),
    path('activate/<rule_id>/', login_required(RuleActivateView.as_view()), name='activate_rule'),
]

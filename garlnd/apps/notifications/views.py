from django.http import Http404
from django.views.generic import ListView
from .models import Notification
from apps.rules.models import Rule


class NotificationsListView(ListView):
    template_name = 'notifications_list.html'
    context_object_name = 'notifications_list'
    paginate_by = 50
    extra_context = {}

    def get_queryset(self, rule_id):
        return Notification.objects.filter(rule_id=rule_id).order_by('-created_at')

    def get(self, request, rule_id, *args, **kwargs):
        try:
            rule = Rule.objects.get(id=rule_id, owner=request.user)
        except Rule.DoesNotExist:
            raise Http404()
        else:

            self.object_list = self.get_queryset(rule_id)
            allow_empty = self.get_allow_empty()

            if not allow_empty:
                # When pagination is enabled and object_list is a queryset,
                # it's better to do a cheap query than to load the unpaginated
                # queryset in memory.
                if (self.get_paginate_by(self.object_list) is not None
                    and hasattr(self.object_list, 'exists')):
                    is_empty = not self.object_list.exists()
                else:
                    is_empty = len(self.object_list) == 0
                if is_empty:
                    raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.")
                            % {'class_name': self.__class__.__name__})

            self.extra_context.update({'rule': rule})
            context = self.get_context_data()
            return self.render_to_response(context)


    def get_context_data(self, **kwargs):
        context = super(self.__class__, self).get_context_data(**kwargs)
        for key, value in self.extra_context.items():
            if callable(value):
                context[key] = value()
            else:
                context[key] = value
        return context
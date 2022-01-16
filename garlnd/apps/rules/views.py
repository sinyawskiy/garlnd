from json import dumps

from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.http import Http404, HttpResponseBadRequest, HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from django.views.generic import View, ListView, DeleteView
from .forms import RuleForm
from .models import Rule


class RulesListView(ListView):
    template_name = 'rules_list.html'
    context_object_name = 'rules_list'
    paginate_by = 25

    def get_queryset(self):
        return Rule.objects.filter(owner=self.request.user)


class RuleEditView(View):
    def get(self, request, rule_id):
        try:
            rule = Rule.objects.get(id=rule_id)
        except Rule.DoesNotExist:
            raise Http404()
        else:
            if rule.owner == request.user:
                rule_form = RuleForm(request=request, instance=rule)
                return render(request, 'rule_form.html', {
                    'rule_id': rule.id,
                    'rule_form': rule_form,
                    'initial_map_zoom': settings.DEFAULT_MAP_ZOOM,
                    'initial_longitude': settings.DEFAULT_MAP_LONGITUDE,
                    'initial_latitude': settings.DEFAULT_MAP_LATITUDE,
                    'change': True,
                })
            else:
                return HttpResponseBadRequest()

    def post(self, request, rule_id):
        try:
            rule = Rule.objects.get(id=rule_id)
        except Rule.DoesNotExist:
            raise Http404()
        else:
            if rule.owner == request.user:
                rule_form = RuleForm(request=request, data=request.POST, files=request.FILES, instance=rule)
                if rule_form.is_valid():
                    edited_rule = rule_form.save(commit=False)
                    edited_rule.save()

                    return HttpResponseRedirect(reverse('rules_list'))
                else:
                    return render(request, 'rule_form.html', {
                        'rule_id': rule.rule.id,
                        'rule_form': rule_form,
                        'change': True,
                    })
            else:
                return HttpResponseBadRequest()


class RuleAddView(View):
    def get(self, request):
        if request.user.max_rules_count is None or Rule.objects.filter(owner=request.user).count() < request.user.max_rules_count:
            return render(request, 'rule_form.html', {
                'rule_form': RuleForm(request=request),
                'initial_map_zoom': settings.DEFAULT_MAP_ZOOM,
                'initial_longitude': settings.DEFAULT_MAP_LONGITUDE,
                'initial_latitude': settings.DEFAULT_MAP_LATITUDE
            })
        else:
            return HttpResponseRedirect(reverse('rules_list'))

    def post(self, request):
        if request.user.max_rules_count is None or Rule.objects.filter(owner=request.user).count() < request.user.max_rules_count:
            rule_form = RuleForm(request=request, data=request.POST)
            if rule_form.is_valid():
                added_rule = rule_form.save(commit=False)
                added_rule.owner = request.user
                added_rule.save()

                return HttpResponseRedirect(reverse('rules_list'))
            else:
                return render(request, 'rule_form.html', {
                    'rule_form': rule_form,
                })
        else:
            return HttpResponseRedirect(reverse('rules_list'))


class RuleDeleteView(DeleteView):
    template_name = 'rule_confirm_delete.html'
    model = Rule
    success_url = reverse_lazy('rules_list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(RuleDeleteView, self).get_object()
        if not obj.owner == self.request.user:
            return HttpResponseBadRequest()
        return obj


class RuleActivateView(View):
    def post(self, request, rule_id):
        try:
            rule = Rule.objects.get(id=rule_id)
            ac = rule.activated_at
            de = rule.deactivated_at

        except Rule.DoesNotExist:
            raise Http404()
        else:
            if rule.owner == request.user:
                rule.is_active = not rule.is_active
                rule.save()

                return HttpResponse(dumps({
                    'deactivated_at': rule.deactivated_at.strftime('%Y-%m-%d %H:%M:%S') if rule.deactivated_at else '-', # #.replace(tzinfo=utc_tz).astimezone(get_current_timezone()).strftime('%Y-%m-%d %H:%M:%S')
                    'activated_at': rule.activated_at.strftime('%Y-%m-%d %H:%M:%S'),
                }), content_type='application/json')

            raise Http404

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.template import Context
from django.template.loader import get_template
from django.views.generic import FormView, TemplateView
from apps.account.forms import FeedbackForm
from apps.maps.models import Map


class MainPageView(TemplateView):
    template_name = 'main.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context.update({
            'show_demo_map': Map.objects.filter(Q(Q(id=1)&Q(Q(view_password=None)|Q(view_password='')))).exists()
        })
        print(context)
        return self.render_to_response(context)


class FeedbackView(FormView):
    form_class = FeedbackForm
    template_name = 'feedback.html'
    success_url = None

    def get_success_url(self):
        return reverse('main')

    def get_form(self, form_class):
        if not self.request.user.is_anonymous and self.request.user.is_authenticated:
            return form_class(email=self.request.user.email, **self.get_form_kwargs())
        return form_class(**self.get_form_kwargs())

    def get(self, request, *args, **kwargs):
        self.request = request
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        self.request = request
        return super(FeedbackView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        user_email = form.cleaned_data['email']
        user_subject = form.cleaned_data['subject']
        text = form.cleaned_data['text']

        browser_info = 'IP адрес: %s, браузер: %s' % (self.request.META['HTTP_HOST'], self.request.META['HTTP_USER_AGENT'])
        user_info = 'Пользователь не авторизован'
        if self.request.user.is_authenticated():
            user_info = 'Пользователь ID:%d %s' % (self.request.user.id, self.request.user.email)

        message_context = Context({'text': text, 'user_subject': user_subject, 'user_email': user_email, 'browser_info': browser_info, 'user_info': user_info})

        message_text_template = get_template('feedback_email.txt')
        message_text = message_text_template.render(message_context)
        message_html_template = get_template('feedback_email.html')
        message_html = message_html_template.render(message_context)

        msg = EmailMultiAlternatives('Сообщение в службу поддержки', message_text, settings.EMAIL_ADDRESS_FROM, (settings.FEEDBACK_MAIL_TO,))
        msg.attach_alternative(message_html, "text/html")

        if form.cleaned_data['attachment']:
            attachment = self.request.FILES['attachment']
            msg.attach(attachment.name, attachment.file.read(), attachment.content_type)

        msg.send()
        return HttpResponseRedirect(self.get_success_url())

from django.views.generic import TemplateView
from connection.models import Contact
from django.shortcuts import render
from django_messages.models import inbox_count_for

def IndexPageView(request,template_name = 'main/index.html'):

    ctx = {}
    if request.user.is_authenticated:
        ctx['requests_count'] = Contact.objects.unread_request_count(request.user)
    return render(request, template_name, ctx)

class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'

class MessagesView(TemplateView):
    template_name = 'main/messages.html'

class ConnectionsView(TemplateView):
    template_name = 'main/connections.html'

class AccountView(TemplateView):
    template_name = 'main/account_update.html'

class QuestionsView(TemplateView):
    template_name = 'main/questions.html'

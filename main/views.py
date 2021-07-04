from django.views.generic import TemplateView


class IndexPageView(TemplateView):
    template_name = 'main/index.html'

class ChangeLanguageView(TemplateView):
    template_name = 'main/change_language.html'

class ProfileView(TemplateView):
    template_name = 'main/profile.html'

class MessagesView(TemplateView):
    template_name = 'main/messages.html'

class ConnectionsView(TemplateView):
    template_name = 'main/connections.html'

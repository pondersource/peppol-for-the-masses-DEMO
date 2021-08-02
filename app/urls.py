from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

# from iommi import Form
from django.contrib.auth.models import User

from main.views import IndexPageView, ChangeLanguageView , MessagesView , ProfileView , ConnectionsView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', IndexPageView.as_view(), name='index'),
    path('profile/', ProfileView.as_view(), name='profile'),

    path('i18n/', include('django.conf.urls.i18n')),
    path('language/', ChangeLanguageView.as_view(), name='change_language'),

    path('accounts/', include('accounts.urls')),
    path('django_messages/', include('django_messages.urls'), name="django_messages"),
    path('connection/', include('connection.urls') , name="connection"),
    path('quickbooks/', include('quickbooks.urls', namespace="quickbooks")),
    #path('SOAP_client/', include('SOAP_client.urls', namespace="SOAP_client")),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

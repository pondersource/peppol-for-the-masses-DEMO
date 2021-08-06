from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static

# from iommi import Form
from django.contrib.auth.models import User

from main.views import IndexPageView, ChangeLanguageView , MessagesView , ConnectionsView , AccountView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', IndexPageView.as_view(), name='index'),

    path('i18n/', include('django.conf.urls.i18n')),
    path('language/', ChangeLanguageView.as_view(), name='change_language'),

    path('accounts/', include('accounts.urls')),
    path('account/', AccountView.as_view(), name='account'),
    path('django_messages/', include('django_messages.urls'), name="django_messages"),
    path('connection/', include('connection.urls') , name="connection"),
    path('quickbooks/', include('quickbooks.urls', namespace="quickbooks")),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

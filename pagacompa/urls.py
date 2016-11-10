"""map URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from pay import views, infopages, pago

urlpatterns = [
    
    url(r'^admin/', admin.site.urls),
    
    url(r'^$', views.index),
    url(r'^login$', views.entrar),
    url(r'^logout$', views.salir),
    url(r'^olvido$', views.olvido),
    
    url(r'^registro$', views.registro),
    url(r'^panel$', views.panel),
    
    url(r'^perfil$', views.perfil),

    url(r'^api/renew$', infopages.api_renew),
    url(r'^api/create$', infopages.api_create),
    url(r'^api/query$', infopages.api_query),
    url(r'^api/info$', infopages.api_info),

    # URL DE PAGO
    url(r'^(.{10})$', pago.view),

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.generic.base import TemplateView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from home import views as home_views
# as per https://puput.readthedocs.io/en/latest/setup.html
from puput import urls as puput_urls
from allauth import urls as allauth_urls

urlpatterns = [
    path('django-admin/', admin.site.urls),

    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),

    path('search/', search_views.search, name='search'),

    path('contents/', home_views.contents),
    path('feast/<slug:fcode>/', home_views.feast),
    path('chant/<slug:hcode>/', home_views.chant),
    path('index/<slug:opart>/', home_views.index),
    path('index/', home_views.index),
    path('edit_proposal/<slug:hcode>/', home_views.edit_proposal),
    path('edit_proposal/<slug:hcode>/<slug:cloned>/', home_views.edit_proposal),
    path('proposal/<slug:hcode>/<slug:submitter>/', home_views.proposal),
    path('select/<slug:hcode>/<slug:submitter>/', home_views.select),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain") ),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(allauth_urls)),
    path("", include(puput_urls)),
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]

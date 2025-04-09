from django.urls import re_path, include
from . import views
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.contrib.auth import views as auth_views


admin.site.site_header = "CoolRoof"
admin.site.site_title = "CBS"
admin.site.index_title = "Home"
 
urlpatterns = [
    re_path(r'^admin/',admin.site.urls),
    re_path(r'^$', views.CoolRoof),

    re_path(r'^CoolRoof/',views.CoolRoof,name='CoolRoof'),
    re_path(r'^index_page/?$', views.index_page,name='index_page'),
    re_path(r'^coolroof/detailed/$',views.coolroof_detailed, name='coolroof_detailed'),
    re_path(r'^coolroof/parametric/$',views.coolroof_parametric, name='coolroof_parametric'),
    # re_path(r'^Coolroof/',views.coolroof),
    #re_path(r'^Coolroof_detailed/',views.coolroof_detailed),
    #re_path(r'^Coolroof_parametric/',views.coolroof_parametric),
    re_path(r'^submitform/?$', views.simple),
    
    re_path(r'^submitform_detailed/?$', views.detailed),
    re_path(r'^submitform_parametric/?$', views.parametric),
    re_path(r'^status/(?P<pk>[0-9]+)/$', views.getCompletionStatus),
    re_path(r'^display_results/(?P<pk>[0-9]+)/$', views.redirectResults),
    re_path(r'^status_simple/(?P<pk>[0-9]+)/$', views.getCompletionStatusSimple),
    re_path(r'^display_results_simple/(?P<pk>[0-9]+)/$', views.redirectResultsSimple),
    re_path(r'^display_results_parametric/(?P<pk>[0-9]+)/$', views.redirectResultsParametric),
    re_path(r'^status_parametric/(?P<pk>[0-9]+)/$', views.getCompletionStatusParametric),
    re_path(r'^create_user/$',views.create_user),
    re_path(r'^glossary/$',views.glossary),
    re_path(r'^email/$',views.email),
    re_path(r'^login_register/$',views.login_register, name = "login_register"),
    re_path(r'^login_user/$',views.login_user, name = "login_user"),
    re_path(r'^logout_user/$',views.logout_user, name="logout_user"),
    re_path(r'^projects_page/$',views.projects_page,name="projects_page"),
    re_path(r'^accounts/', include('django.contrib.auth.urls')),
    re_path(r'^home/$', TemplateView.as_view(template_name='home.html'),name='home'), # new
    re_path(r'^signup/$', views.signup, name='signup'),
    re_path(r'^password_reset/$', auth_views.PasswordResetView.as_view(), name='password_reset'),
    re_path(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'^edit_page/(?P<pk>[0-9]+)/$', views.edit_page, name = "edit_page"),
    re_path(r'^edit_page_detailed/(?P<pk>[0-9]+)/$', views.edit_page_detailed, name = "edit_page_detailed"),
    re_path(r'^edit_page_parametric/(?P<pk>[0-9]+)/$', views.edit_page_parametric, name = "edit_page_parametric"),
    #re_path(r'^html/$', views.html_redirect),
    # re_path(r'oracle/?$', views.oracle_event),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

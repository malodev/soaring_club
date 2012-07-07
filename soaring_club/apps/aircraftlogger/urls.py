from django.conf.urls.defaults import * #@UnusedWildImport
from django.contrib import databrowse #@UnusedImport
from django.contrib.auth.decorators import login_required #@UnusedImport
import os #@UnusedImport
from django.views.generic.list_detail import object_detail #@UnusedImport
from models import * #@UnusedWildImport



urlpatterns = patterns('aircraftlogger.views',
    # Example:
    url(r'^meta/$', 'display_meta'),
    url(r'^logs/$', 'logs'),
    url(r'^flarms/$', 'flarm_db'),    
    url(r'^flarm/(?P<flarm_id>[A-Za-z0-9]{6})/$', 'flarm_db'),
    url(r'^flarm/(?P<flarm_id>[A-Za-z0-9]{6})/(?P<date>\d{4}-\d{2}-\d{2})/$', 'flarm_db'),
    url(r'^$', 'index'),
    
)

#flight
urlpatterns += patterns('aircraftlogger.views',
    url(r'^sheet/$', 'flights_sheet'),
    url(r'^flights/$', 'flights'),
    url(r'^flights/(?P<flight_id>\d+)/$', 'update_flight_landing'),
    url(r'^flights/(?P<role>\w+)/$', 'flights'),
    url(r'^bills/$', 'flights_bills'),
    url(r'^bills/(?P<flight_id>\d+)/$', 'update_flight_landing'),
    url(r'^receipts/$', 'receipts'),
    url(r'^receipts/(?P<receipt_id>\d+)/$', 'update_receipt_note'),
    url(r'^reports/$', 'reports'),
    url(r'^reports/(?P<action>\w+)/$', 'reports'),
    url(r'^reports/debits/(?P<member_id>\d+)/$', 'set_member'),
    
)


urlpatterns += patterns('',
    #url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'media'), 'show_indexes':True}),
    #(r'^aircraftlogger/media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
    url(r'^favicon.ico$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), 'static/images/favicon.ico')}),
)

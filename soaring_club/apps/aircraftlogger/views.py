from django.http import HttpResponse, Http404
from django.db.models import Q #@UnusedImport
from django.shortcuts import render
from django.shortcuts import  redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.exceptions import  ObjectDoesNotExist #@UnusedImport
from django.conf import settings #@UnusedImport
from django.views.generic import View
from django.views.generic.edit import FormMixin
from django.utils import simplejson as json
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

import decimal
import towerlog
from django.utils.log import getLogger
from forms import * #@UnusedWildImport
from models import * #@UnusedWildImport

logger = getLogger('app')

class JSONResponseMixin(object):
    def render_to_response(self, context):
        "Returns a JSON response containing 'context' as payload"
        return self.get_json_response(self.convert_context_to_json(context))

    def get_json_response(self, content, **httpresponse_kwargs):
        "Construct an `HttpResponse` object."
        return HttpResponse(content,
                                 content_type='application/json',
                                 **httpresponse_kwargs)

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


class JSONFormView(FormMixin, View, JSONResponseMixin):
    success_message = ''

    def form_valid(self, form, request):
        form.save()
        return self.success(_(self.success_message))
    
    def form_invalid(self, form):
        response = SimpleResponse()
        response.setError(_("Validation failed."))
        response.setData(form.errors)
        return self.render_to_response(response.json())
    
    def success(self, message):
        response = SimpleResponse()
        response.setSuccess(message)
        return self.render_to_response(response.json()) 
    
    def get(self, request, *args, **kwargs):
        raise Http404
    
    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class()) #@UnusedVariable


class SimpleResponse(object):
    """
    The simplest form of our ajax response
    """
    def __init__(self, error=False, message=None):
        self.error = error
        self.message = message
        self.data = {}
    
    def setError(self, message):
        self.error = True
        self.message = message
        
    def setSuccess(self, message):
        self.error = False
        self.message = message
    
    def setData(self,data={}):
        self.data = data.copy()
    
    def json(self):
        return {'error': self.error,
                'message': self.message,
                'data':self.data
                } 


def get_planes_from_flarm(flarm_id, date=None):
    """
    Get the planes with a particolar flarm installed. If date is specified 
    select only planes that don't removed flarm until that date
    """
    planes = Plane.objects.filter( Q(installation__flarmid__iexact=flarm_id))
    if planes and date:
        planes.filter(Q(installation__date_added__lte=date),
                      Q(installation__date_removed__gte=date) | 
                      Q(installation__date_removed__isnull=True)
                     )
    return planes
    
def get_current_member(request, stuff_allowed=True):
    """
    Get the current logged member or if the user is staff the member choosed 
    via cookie
    """
    member = None
    if request.user.is_authenticated():
        if request.session.get('member', False) and stuff_allowed and request.user.is_staff:
            member = request.session['member']
        #Is there a better solution to check if user has an associated member?
        elif request.user.member.count():
            member = request.user.member.get()
    return member

def index(request):
    """
    Main page.
    Show login botton or memebr status after login.
    """
    membercredit = tow_cents = tmg_cents = tow_good_status = tmg_good_status =  None
    member = get_current_member(request)
    balance = []
    if member:
        membercredit = member.membercredit_or_none
        for cls, dsc in CREDIT_CLASSES:
            b = member.balance(cls)
            if b:
                balance.append((dsc,b,b>0))
        tow_cents = member.tow_cents_balance()
        if tow_cents > 0:
            tow_good_status = True
        tmg_cents = member.tmg_cents_balance()
        if tmg_cents > 0:
            tmg_good_status = True
        logged = request.user
    else:
        logged = False

    return render(request, 'index.html', {'logged' : logged,
                                                         'member' : member,
                                                         'membercredit' : membercredit,
                                                         'balance' : balance,
                                                         'tow_cents' : tow_cents,
                                                         'tow_good_status' : tow_good_status,
                                                         'tmg_cents' : tmg_cents,
                                                         'tmg_good_status' : tmg_good_status,
                                                          })

def display_meta(request):
    values = request.META.items()
    values.sort()
    html = []
    for k, v in values:
        html.append('<tr><td>%s</td><td>%s</td></tr>' % (k, v))
    return HttpResponse('<table>%s</table>' % '\n'.join(html))

def logs(request):
    """
    This view show flights logged in one Tower Station log file and permit to add them to Flights object
    """
    if request.method == 'POST':
        #A form has been submitted
        if request.POST.has_key('file_log'):
            log_selection = TowerLogForm(request.POST)
            if log_selection.is_valid():
                tower_log = get_object_or_404(TowerLog,
                            id=log_selection.cleaned_data['file_log'])
                nome = tower_log.log_file.name
                nmea = towerlog.TowerLog()
                nmea.process_file(tower_log.log_file)
                logs = sorted(list(nmea.generate_log_book()), key=lambda record: record[2])
                for log in logs:
                    planes = get_planes_from_flarm(log[1])
                    log.append(planes)
                return render(request, 'logs.html', {
                                            'log_selection': log_selection,
                                            'nome': nome,
                                            'logs': logs})
        else:
            if request.POST.has_key('flights'):
                flights = request.POST.getlist('flights')
                flights = [ fly.split(',') for fly in flights ]
                debug_print('to flights.html--->',flights)
                return render(request, 'flights.html',
                                        {
                                            'flights': flights,
                                        })
    log_selection = TowerLogForm()
    return render(request, 'logs.html', {'log_selection': log_selection})


def member_flights(role, member, request, paginator=None):
    flights_missing = flights_durations = first_date = flights_page = flights_from = flights_to = None
    flights_list = []
    form_range_flights = DateRangeForm()
    form_year = YearChooseForm()
    if member:
        if request.method == 'POST' and request.POST.has_key('from_date'):
            form_range_flights = DateRangeForm(request.POST)
            if form_range_flights.is_valid():
                flights_from = form_range_flights.cleaned_data['from_date']
                flights_to = form_range_flights.cleaned_data['to_date']
        try:
            first_date = member.first_flight_date(role, flights_from, flights_to)
            flights_list = member.active_flights(role, flights_from, flights_to)
            flights_missing = member.flights_missing_time_landing(role, flights_from, flights_to).count()
            flights_durations = member.flights_durations(role, flights_from, flights_to)
        except (AttributeError, TypeError):
            pass
        # Make sure page request is an int. If not, deliver first page.
        page = request.GET.get('page')
        try:
            page = int(page)
        except (ValueError, TypeError):
            if page != 'all':
                page = 1

        # If page request (9999) is out of range, deliver last page of results.
        if page == 'all':
            flights_page = flights_list
            is_paginated = True,
            paginator = Paginator(flights_list, flights_list.count()) 
            page = 1
        else:
            is_paginated = True,
            paginator = Paginator(flights_list, 50) # Show 25 contacts per page
        try:
            flights_page = paginator.page(page)
        except (EmptyPage, InvalidPage):
            flights_page = paginator.page(paginator.num_pages)

    return {'role': role,
            'flights': flights_page,
            'is_paginated': is_paginated,
            'paginator': paginator,
            'member' : member,
            'flights_no': flights_list.count(),
            'flights_durations': flights_durations,
            'flights_missing': flights_missing,
            'first_date': first_date,
            'hits' : flights_list.count(),    
            'page': page,
            'pages': paginator.num_pages,
            'results_per_page': paginator.per_page,
            'next' : flights_page.next_page_number(),
            'previous' : flights_page.previous_page_number(),
            'has_next' : flights_page.has_next(),
            'has_previous' : flights_page.has_previous(),
            'form_range_flights' : form_range_flights,
            'form_year' : form_year,
           }


@login_required
def flights(request, role='pilot'):
    member = get_current_member(request)
    return render(request, 'flights.html',  member_flights(role, member, request))


@login_required
def flights_bills(request):
    """
    List flights_bills
    """

    first_date = bills_from = bills_to = None
    bills_list = []
    member = get_current_member(request)
    form_range_flightbills = DateRangeForm()
    if member:
        if request.method == 'POST' and request.POST.has_key('from_date'):
            form_range_flightbills = DateRangeForm(request.POST)
            if form_range_flightbills.is_valid():
                bills_from = form_range_flightbills.cleaned_data['from_date']
                bills_to = form_range_flightbills.cleaned_data['to_date']
        try:
            first_date = member.first_flightbill_date(bills_from, bills_to)
            bills_list = member.active_flightbills(bills_from, bills_to)
            debits = {}
            for cls, dsc in CREDIT_CLASSES:
                debits[dsc] = member.debit(cls, bills_from, bills_to)
        except (AttributeError, TypeError):
            pass

    return render(request, 
                  'flights_bills.html',
                  {
                   'member' : member,
                   'hits' : bills_list.count(),    
                   'first_date': first_date,
                   'bills_list': bills_list,
                   'debits' : debits,
                   'form_range_flightbills' : form_range_flightbills,
                  }
                 )

@login_required
def update_flight_landing(request, flight_id):
    """ 
    Allow user or staff to update landing information for single flight
    TODO: allow staff to update all info
    """
    member = get_current_member(request, stuff_allowed=False)
    if member:
        flight = get_object_or_404(Flight, pk=flight_id)
        if flight in member.pilot.all() or request.user.is_staff:
            form_saved = None
            if request.method == 'POST':
                form = FlightLandingForm(request.POST)
                if form.is_valid():
                    flight.landing = form.cleaned_data['landing']
                    flight.landing_field = form.cleaned_data['landing_field']
                    flight.save()
                    form_saved = True
                return render(request, 'flight_update_landing.html', {'form_saved':form_saved, 'flight':flight, 'form':form})
            else:
                context = {'flight_id': flight.id}
                if flight.landing:
                    context['landing'] = flight.landing
                if flight.landing_field:
                    context['landing_field'] = flight.landing_field 
                form = FlightLandingForm()
                return render(request, 'flight_update_landing.html', {'form_saved':form_saved, 'flight':flight, 'form':form})
        else:
            return redirect('/flights/')
    else:
        return redirect('/')

@login_required
def receipts(request):
    return render(request, 'receipts.html', member_receipts(get_current_member(request)) )

@login_required
def update_receipt_note(request, receipt_id):
    if request.user.is_authenticated():
        if request.user.member.count():
            member = request.user.member.get()
            receipt = get_object_or_404(Receipt, pk=receipt_id)
            if receipt in member.receipt_payer.all() or request.user.is_staff:
                if request.method == 'POST':
                    form_saved = None
                    form = ReceiptNoteForm(request.POST)
                    if form.is_valid():
                        note = form.cleaned_data['note']
                        receipt.note = note
                        receipt.updated_by = request.user
                        receipt.save()
                        form_saved = True
                    return render(request, 'receipt_update_note.html', {'form_saved':form_saved, 'receipt':receipt, 'form':form})
                else:
                    context = {'note': receipt.note}
                    form = ReceiptNoteForm(context)
                    return render(request, 'receipt_update_note.html', {'receipt':receipt, 'form':form})
            else:
                return redirect('/receipts/')
    else:
        return redirect('/')


class ReceiptRangeView(JSONFormView):
    form_class = ReceiptRangeForm
    success_message="FATTO!!"


@login_required
def reports(request, action=None, template=None):
    """
    This view render the 'Report' tab. The URL that is responding to is /reports/action.
    action can be 'debits' for retrieving cents balance, 'receipts' for get a list of 
    receipts in an interval, 'member' to impersonate a member for viewing flights etc..,
    'clearance' to retrieve a list of pilots permitted to flight.   
    """
    #TODO: change word debits in balance
    if request.user.is_authenticated():
        if request.user.is_staff:
            logged = request.user
            form_range_receipts = ReceiptRangeForm()
            form_member = MemberChooseForm()
            form_debits_filter = DebitsForm(initial={'status_filter' : 'Active'})
            context = {'logged' : logged,
                       'form_debits_filter': form_debits_filter,
                       'form_range_receipts': form_range_receipts,
                       'form_member': form_member,
                       'club_limit':settings.MAX_DAYS_FROM_LAST_FLIGHT_CLUB.days,
                       'private_limit':settings.MAX_DAYS_FROM_LAST_FLIGHT_PRIVATE.days,
                      }
            if request.method == 'POST':
                if action == 'debits':
                    #Form for filter debits  
                    form_debits_filter = DebitsForm(request.POST)
                    #Retrieve data only if request is for results template
                    if not request.is_ajax() or template == "debits_table":
                        # tourism, glider tow, motorglider, etc... may be there is a better method to do this...
                        if form_debits_filter.is_valid():
                            #Check what button was pressed and apply related filter to members
                            if form_debits_filter.cleaned_data['status_filter'] == 'Active':
                                report = debits_report(~Q(type__type__exact='inactive'))
                            elif form_debits_filter.cleaned_data['status_filter'] == 'Registered':
                                report = debits_report(Q(type__type__exact='registered'))
                            else:
                                report = debits_report()
                            #Filter report with a credit lesser than settings.MIN_CREDIT in any type of balance:
                            if form_debits_filter.cleaned_data['only_negative']:
                                new_report = []
                                for r in report:
                                    for dsc, d in r['debits']:
                                        if d < settings.MIN_CREDIT:
                                            new_report += [r]
                                            break
                                report = new_report
                            totals = []
                            #Compute totals for every credit classes
                            for cls,dsc in CREDIT_CLASSES:
                                totals += ((dsc, sum([dict(r['debits'])[dsc] for r in report]),),)
                            context.update({
                                           'debits': report,
                                           'totals': totals,
                                          })
                        else:
                            if request.is_ajax():
                                template = 'blank'             
                elif action == 'receipts':
                    #refresh form with POST data 
                    form_range_receipts = ReceiptRangeForm(request.POST)
                    #Retrieve data only if request is for results template
                    if not request.is_ajax() or template == "receipts_table":
                        if form_range_receipts.is_valid():
                            reference_from = form_range_receipts.cleaned_data['reference_from']
                            reference_to = form_range_receipts.cleaned_data['reference_to']
                            receipt_from = Receipt.objects.get(reference=reference_from)
                            receipt_to = Receipt.objects.get(reference=reference_to)
                            try:
                                from_int = int(reference_from)
                                to_int = int(reference_to)
                            except ValueError:
                                from_int = to_int = None
                            receipts = []
                            if from_int and to_int:
                                for ref in range(from_int,to_int+1):
                                    try:
                                        r = Receipt.objects.get(reference=str(ref))
                                    except ObjectDoesNotExist:
                                        r = None
                                    if r:
                                        receipts.append(r)
                            if not receipts:
                                receipts = Receipt.objects.filter(date__lte=receipt_to.date, date__gte=receipt_from.date)
                            total = 0
                            for receipt in receipts:
                                total += receipt.total
                            context.update({
                                            'total':total, 
                                            'receipts':receipts, 
                                            'from':receipt_from.date, 
                                            'to':receipt_to.date,
                                            })
                        else:
                            if request.is_ajax():
                                template = 'blank'             

                elif action == 'member':
                    #refresh form with POST data 
                    form_member = MemberChooseForm(request.POST)
                    #Check if request is for results or for refreshing form
                    #Retrieve data only if request is for results template
                    if not request.is_ajax() or template == "member_table":
                        if form_member.is_valid():
                            member = form_member.cleaned_data['member']
                            request.session['member'] = member
                            context.update({'member':member})
                        else:
                            #form is invalid, clear results
                            if request.is_ajax():
                                template = 'blank'             

                elif action == 'clearance':
                    #There's no need to update form but for avoid data retrieve when call is for form only
                    #check is done
                    #Retrieve data only if request is for results template                   
                    logger.debug("clearance action with path=%s is_ajax=%s template=%s" % (request.get_full_path(),request.is_ajax(), template))
                    if not request.is_ajax() or template == "clearance_table":
                        logger.debug("clearance report")
                        report = clearance_report()
                        context.update({
                                       'clearance': report,
                                      })
                    
                #Update form values
                context.update({
                                'form_debits_filter': form_debits_filter,
                                'form_range_receipts': form_range_receipts,
                                'form_member': form_member,
                              })
            
                
            if template is None:
                template='reports.html'
            else:
                try:
                    template += '.html' 
                    get_template(template)
                except TemplateDoesNotExist:
                    template='reports.html'
            logger.debug(" with request=%s context=%s template=%s" % (request.get_full_path(), context, template))                   
            return render(request, template, context)
    return redirect('/')

def set_member(request, member_id):
    member = Member.objects.get(pk=member_id)
    request.session['member'] = member
    return redirect('/')

def member_receipts(member):
    receipts = total = tow_cents = tmg_cents = first_date = None
    if member:
        try:
            receipts = member.active_receipts()
            tow_cents = member.tow_cents_aquired()
            tmg_cents = member.tmg_cents_aquired()
            total = Receipt.objects.user_total(member.id)
            first_date = member.first_receipt_date()
            _credits = []
            for cls, dsc in CREDIT_CLASSES:
                _credits += ( (dsc, member.credit(cls)), )
            
        except (AttributeError, TypeError):
            pass
    
    return {
            'total':total,
            'tow_cents':tow_cents,
            'tmg_cents':tmg_cents,
            'credits':_credits,
            'first_date':first_date,
            'receipts': receipts,
            'member': member,
              }


@login_required
def flights_sheet_submit(request, form, formset, head, flights):
    logged = request.user
    if logged.is_staff:
        return render(request, 'flights_sheet.html', {'form':form, 'formset': formset})
    else:
        return redirect('/')
    
@login_required
def flights_sheet(request):
    logged = request.user
    saved = False
    if logged.is_staff:
        if request.method == 'POST':
            form = FlightsSheet(request.POST)
            formset = FlightsSheetItemSet(request.POST)
            if form.is_valid() and formset.is_valid():
                head = form.cleaned_data
                flights = formset.cleaned_data
                flight = flights[0]

                #Set the scale for conversion if unit of tow is minutes
                if head['counter_unit'] == 'minutes':
                    scale = decimal.Decimal(str(100.0/60.0))
                else:
                    scale = 1

                #Cerca il socio fittizio che corrisponde al CUS
                payer = Member.objects.get(last_name__exact='CUS')
                #il riscaldamento se c'e' viene contaggiato come volo di servizio
                #ed imputato a cus. Il volo inizia e termina con l'orario di decollo del primo volo.
                if head['warmup_cost']:
                    tow_flight = Flight(date=head['date'], 
                                           takeoff=flight['takeoff'],
                                           takeoff_field='LIDT',
                                           landing=flight['takeoff'],
                                           landing_field='LIDT',
                                           pilot=head['pilot'],
                                           copilot=None,
                                           plane=head['tow'],
                                           porpouse='riscaldamento')
                    tow_flight.save()
                    bill = FlightBill(flight = tow_flight, 
                                      tow_flight = None,
                                      payer = payer,
                                      cost = head['warmup_cost']*scale,
                                      cost_class = 'service')
                    bill.save()

                for flight in flights:
                    if flight:
                        glider_flight = Flight(date=head['date'], 
                                               takeoff=flight['takeoff'],
                                               takeoff_field='LIDT',
                                               landing=flight['landing_glider'],
                                               landing_field='LIDT',
                                               pilot=flight['pilot'],
                                               copilot=flight['instructor'],
                                               plane=flight['glider'],
                                               porpouse=flight['porpouse'])
                        glider_flight.save()
                        if 'scheda' in flight['porpouse']:
                            porpouse = 'traino scuola'
                        else:
                            porpouse = 'traino'
                        tow_flight = Flight(date=head['date'], 
                                               takeoff=flight['takeoff'],
                                               takeoff_field='LIDT',
                                               landing=flight['landing'],
                                               landing_field='LIDT',
                                               pilot=head['pilot'],
                                               copilot=None,
                                               plane=head['tow'],
                                               porpouse=porpouse)
                        tow_flight.save()
                        bill = FlightBill(flight = tow_flight, 
                                          tow_flight = glider_flight,
                                          payer = flight['pilot'],
                                          cost = flight['tow_cost']*scale,
                                          cost_class = 'towing')
                        bill.save()
                        saved = True           
            return render(request, 'flights_sheet.html', {'form':form, 'formset': formset, 'saved':saved})
        else:
            form = FlightsSheet()
            formset = FlightsSheetItemSet()
        return render(request, 'flights_sheet.html', {'form':form, 'formset': formset, 'saved':saved})
    else:
        return redirect('/')
        


# def update_flight(request, object_id):
#     return update_object(request, object_id=object_id, model=Flight, extra_context={'flight':get_object_or_404(Flight, pk=object_id)})

def flarm_db(request, flarm_id=None, date=None):
    if flarm_id and date:
        planes = get_planes_from_flarm(flarm_id, date)
        return render(request, 'flarms.html', {'planes':planes})
    elif flarm_id:
        planes = get_planes_from_flarm(flarm_id)
        return render(request, 'flarms.html', {'planes':planes})
    else:
        planes = Plane.objects.filter(installation__id__isnull=False)
        return render(request, 'flarms.html', {'planes':planes})



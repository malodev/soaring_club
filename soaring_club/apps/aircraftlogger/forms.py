from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from django.forms.util import ErrorList
from django.db.models import Q, Min, Max
from models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import widgets as adminwidgets
from datepicker.widgets import  DatepickerDateInput, TimepickerTimeInput
from django.conf import settings
from django.core.exceptions import  ObjectDoesNotExist
import datetime

    
class MemberForm(ModelForm):
    class Meta:
        model = Member
    
class ReceiptForm(ModelForm):
    class Meta:
        model = Receipt

class ReceiptNoteForm(forms.Form):
    note = forms.CharField(widget=forms.Textarea(attrs={'cols':'70', 'rows':'2'}), label=_('Member Note'))
        
class MemberChooseForm(forms.Form):
    member = forms.ModelChoiceField(queryset=Member.objects.all(), label=_('Member'))

class CheckIfForm(forms.Form):
    istrue = forms.BooleanField(label=_('Only member with negative balance'), required=False)

class YearChooseForm(forms.Form):
    maxmin = Flight.objects.aggregate(min_date=django.db.models.Min('date'), max_date=django.db.models.Max('date'))
    miny = maxmin['min_date'].year
    maxy = maxmin['max_date'].year
    years = [ (y, str(y)) for y in range(miny, maxy+1)]
    year = forms.IntegerField(widget=forms.Select(choices=years), label=_('Year'))

class ReceiptRangeForm(forms.Form):
    reference_from = forms.CharField(label=_('From reference'), required=True)
    reference_to = forms.CharField(label=_('To reference'), required=True)

    def clean(self):
        cleaned_data = self.cleaned_data
        reference_from = cleaned_data.get("reference_from")
        reference_to = cleaned_data.get("reference_to")
        receipt_from = receipt_to = None
        if reference_from:
            try:
                receipt_from = Receipt.objects.get(reference=reference_from)
            except ObjectDoesNotExist:
                msg = _("Receipt does not exist")
                self._errors["reference_from"] = ErrorList([msg])
                del cleaned_data["reference_from"]
        if reference_to:
            try:
                receipt_to = Receipt.objects.get(reference=reference_to)
            except ObjectDoesNotExist:
                msg = _("Receipt does not exist")
                self._errors["reference_to"] = ErrorList([msg])
                del cleaned_data["reference_to"]
        if receipt_from and receipt_to:
            if receipt_from.date > receipt_to.date:
                msg = _("Receipt from come after receipt to. Check values")
                self._errors["reference_from"] = ErrorList([msg])
                self._errors["reference_to"] = ErrorList([msg])
                del cleaned_data["reference_from"]
                del cleaned_data["reference_to"]
        # Always return the full receiption of cleaned data.
        return cleaned_data    

class DateRangeForm(forms.Form):
    from_date = forms.DateField(widget=DatepickerDateInput(attrs={'class':'date'}), label=_('From date'))
    to_date = forms.DateField(widget=DatepickerDateInput(attrs={'class':'date'}), label=_('To date'))

    def clean(self):
        cleaned_data = self.cleaned_data
        from_date = cleaned_data.get("from_date")
        to_date = cleaned_data.get("to_date")
        if from_date and to_date:
            if from_date > to_date:
                msg = _("From date come after to date. Check values")
                self._errors["from_date"] = ErrorList([msg])
                self._errors["to_date"] = ErrorList([msg])
                del cleaned_data["from_date"]
                del cleaned_data["to_date"]
        # Always return the full receiption of cleaned data.
        return cleaned_data
        
    class Media:
        css = { 'screen': ( settings.MEDIA_URL+"jquery/css/jquery-ui-1.7.2.custom.css",
	                        settings.MEDIA_URL+"jquery/css/jquery.timepickr.css",
	                      )
        }
        js = (settings.MEDIA_URL+"jquery/jquery-1.3.2.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-1.7.2.custom.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-i18n.min.js",
              settings.MEDIA_URL+"jquery/ui.timepickr.min.js",
              settings.MEDIA_URL+"datepicker/datepicker.js",
             )
        
    
class ReceiptDetailGenericForm(ModelForm):
    class Meta:
        model = ReceiptDetailGeneric

class PlaneForm(ModelForm):
    class Meta:
        model = Plane

class FlightForm(ModelForm):
    date = forms.DateField(widget=DatepickerDateInput(attrs={'class':'date'}), label=_('Date'))
    takeoff = forms.TimeField(widget=TimepickerTimeInput(attrs={'class':'takeoff'}), label=_('Takeoff'))
    takeoff_field = forms.CharField(max_length=5, initial=settings.HOME_AIRPORT, required=False, label=_('Takeoff field'))
    landing = forms.TimeField(widget=TimepickerTimeInput(attrs={'class':'landing'}), label=_('Landing'))
    landing_field = forms.CharField(max_length=5, initial=settings.HOME_AIRPORT, required=False, label=_('Landing field'))
    class Meta:
        model = Flight
        
    class Media:
        css = { 'screen': ( settings.MEDIA_URL+"jquery/css/jquery-ui-1.7.2.custom.css",
	                        settings.MEDIA_URL+"jquery/css/jquery.timepickr.css",
	                      )
        }
        js = (settings.MEDIA_URL+"jquery/jquery-1.3.2.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-1.7.2.custom.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-i18n.min.js",
              settings.MEDIA_URL+"jquery/ui.timepickr.min.js",
              settings.MEDIA_URL+"datepicker/datepicker.js",
             )

class FlightLandingForm(forms.Form):
#     date_from = forms.DateField(widget=DatepickerDateInput(attrs={'class':'date'}), label=_('From date'))
#     date_to = forms.DateField(widget=DatepickerDateInput(attrs={'class':'date'}), label=_('To date'))
#    flight_id = forms.IntegerField(widget=forms.HiddenInput());
    landing = forms.TimeField(widget=TimepickerTimeInput(attrs={'class':'landing'}), label=_('Landing'))
    landing_field = forms.CharField(max_length=5, initial=settings.HOME_AIRPORT, required=False, label=_('Landing field'))

#     def clean(self):
#         cleaned_data = self.cleaned_data
#         landing = cleaned_data.get("landing")
#         flight_id = cleaned_data.get("flight_id")
#         try:
#             flight = Flight.objects.get(pk=flight_id)
#         except ObjectDoesNotExist:
#             flight = None
# 
#         if flight and landing and landing < flight.takeoff:
#             msg = _("Landing is before takeoff. Check values")
#             self._errors["landing"] = ErrorList([msg])
#             del cleaned_data["landing"]
#         # Always return the full receiption of cleaned data.
#         return cleaned_data    


    class Media:
        css = { 'screen': ( settings.MEDIA_URL+"jquery/css/jquery-ui-1.7.2.custom.css",
	                      )
        }
        js = (settings.MEDIA_URL+"jquery/jquery-1.3.2.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-1.7.2.custom.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-i18n.min.js",
              settings.MEDIA_URL+"datepicker/datepicker.js",
             )

class FlightFilterForm(forms.Form):
    landing = forms.TimeField(widget=TimepickerTimeInput(attrs={'class':'landing'}), required=True, label=_('Landing'))
    landing_field = forms.CharField(max_length=20, initial=settings.HOME_AIRPORT, required=True, label=_('Landing field'))
    class Media:
        css = { 'screen': ( settings.MEDIA_URL+"jquery/css/jquery-ui-1.7.2.custom.css",
	                        settings.MEDIA_URL+"jquery/css/jquery.timepickr.css",
	                      )
        }
        js = (settings.MEDIA_URL+"jquery/jquery-1.3.2.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-1.7.2.custom.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-i18n.min.js",
              settings.MEDIA_URL+"jquery/ui.timepickr.min.js",
             )
        

        
class PilotForm(forms.Form):
    pilot = forms.ModelChoiceField(queryset=Member.objects.filter(type__type__in=('glider_pilot',)), label=_('Pilot'))


class FlightBillItem(forms.Form):
    date = forms.DateField(widget=DatepickerDateInput(attrs={'class':'date'}), required=True, label=_('Date'))
    takeoff = forms.TimeField(widget=forms.TimeInput(attrs={'class':'takeoff hh-mm'}), required=True, label=_('Takeoff'))
    landing = forms.TimeField(widget=forms.TimeInput(attrs={'class':'landing hh-mm', }), required=True, label=_('Landing'))
    pilot = forms.ModelChoiceField(queryset=Member.objects.filter(type__type__in=('glider_pilot', 'student')), required=True, label=_('Pilot'))
    instructor = forms.ModelChoiceField(queryset=Member.objects.filter(type__type__in=('instructor',)), label=_('Instructor'))
    plane = forms.ModelChoiceField(queryset=Plane.objects.exclude(type__in=('tmg',)), required=True, label=_('Plane'))
    
    pass



class FlightsSheetItem(forms.Form):
    glider = forms.ModelChoiceField(queryset=Plane.objects.filter(type__in=('glider','self-launching')), required=True, label=_('Glider'))    
    pilot = forms.ModelChoiceField(queryset=Member.objects.filter(type__type__in=('glider_pilot', 'student')), required=True, label=_('Pilot'))
    instructor = forms.ModelChoiceField(queryset=Member.objects.filter(type__type__in=('instructor',)), required=False, label=_('Instructor'))
    takeoff = forms.TimeField(widget=forms.TimeInput(attrs={'class':'takeoff hh-mm'}), required=True, label=_('Takeoff'))
    landing = forms.TimeField(widget=forms.TimeInput(attrs={'class':'landing hh-mm', }), required=True, label=_('Landing'))
    tow_cost = forms.DecimalField(widget=forms.TextInput(attrs={'class':'tow_cost', }), required=True, max_digits=5, decimal_places=2, label=_('Tow Cost'))
    porpouse = forms.CharField(widget=forms.TextInput(attrs={'class':'note', }), required=True, label=_('Porpouse'))
    landing_glider = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'class':'landing_glider hh-mm'}), label=_('Glider Landing'))

FlightsSheetItemSet = formset_factory(FlightsSheetItem, extra=20)

class FlightsSheet(forms.Form):
    date = forms.DateField(widget=DatepickerDateInput(attrs={'class':'date'}), required=True, label=_('Date'))
    tow = forms.ModelChoiceField(queryset=Plane.objects.filter(type__in=('propeller',)), required=True, label=_('Tow Plane')) 
    pilot = forms.ModelChoiceField(queryset=Member.objects.filter(type__type__in=('tow_pilot',)), required=True, label=_('Tow Pilot'))
    warmup_cost = forms.DecimalField(max_digits=5, decimal_places=2, required=False, label=_('Warmup Cost'))
    counter_unit = forms.TypedChoiceField(choices=(('cents',_('Cents')),('minutes',_('Minutes'))), initial='cents', label=_('Counter unit'))       

    class Media:
        css = { 'screen': ( settings.MEDIA_URL+"jquery/css/jquery-ui-1.7.2.custom.css",
	                        settings.MEDIA_URL+"jquery/css/jquery.timepickr.css",
	                      )
        }
        js = (settings.MEDIA_URL+"jquery/jquery-1.3.2.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-1.7.2.custom.min.js",
              settings.MEDIA_URL+"jquery/jquery-ui-i18n.min.js",
              settings.MEDIA_URL+"jquery/ui.timepickr.min.js",
              settings.MEDIA_URL+"datepicker/datepicker.js",
             )

    
class OwnershipForm(ModelForm):
    class Meta:
        model = Ownership

class InstallationForm(ModelForm):
    class Meta:
        model = Installation

class MemberCreditForm(ModelForm):
    class Meta:
        model = MemberCredit
 
class TowerLogForm(forms.Form):
    file_log = forms.IntegerField(widget=forms.Select(choices =
           [(f.id, f.created.isoformat(' ')) for f in TowerLog.objects.order_by('created')]))


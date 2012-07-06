from django.contrib import admin
from django.contrib.contenttypes import generic
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from soaring_club.aircraftlogger.models import *
from soaring_club.settings import *

class InstallationInline(admin.TabularInline):
    model = Installation
    extra = 1
    
class InstallationAdmin(admin.ModelAdmin):
    list_display = ('plane', 'flarm', 'flarmid', 'date_added', 'date_removed')    
admin.site.register(Installation, InstallationAdmin)

class OwnershipInline(admin.TabularInline):
    model = Ownership
    extra = 1
        
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('plane', 'owner', 'date_purchased', 'date_sold')    
admin.site.register(Ownership, OwnershipAdmin)



class MemberTypeInline(generic.GenericTabularInline):
    model = MemberType
    extra = 2
#admin.site.register(MemberType)

class MemberAdmin(admin.ModelAdmin):
    prepopulated_fields = {'sort_name' : ('last_name', 'first_name')}
    list_display = ('last_name', 'first_name', 'user', 'types', 'email', 'notes')
    inlines = [OwnershipInline,MemberTypeInline,]
    search_fields = ('last_name', 'first_name', 'type__type')

admin.site.register(Member, MemberAdmin)

class PlaneAdmin(admin.ModelAdmin):
    list_display = ('type', 'regmark', 'manufacturer', 'model', 'owners_str')
    list_display_links = ('regmark', )
    list_filter = ('type',)
    inlines = [InstallationInline, OwnershipInline]
admin.site.register(Plane, PlaneAdmin)

class FlarmAdmin(admin.ModelAdmin):
    inlines = [InstallationInline,]   
    extra = 1
admin.site.register(Flarm, FlarmAdmin)

class FlightBillInline(admin.TabularInline):
    model = FlightBill
    verbose_name = verbose_name_plural = 'Flight bill'
    fk_name = 'flight'
    extra = 1

class GliderFlightInline(admin.TabularInline):
    model = FlightBill
    verbose_name = verbose_name_plural = 'Glider flight'
    fk_name = 'tow_flight'
    extra = 1


class FlightAdminForm(forms.ModelForm):
    takeoff_field = forms.CharField(max_length=20, initial=HOME_AIRPORT, required=False, label=_('Takeoff field'))
    landing_field = forms.CharField(max_length=20, initial=HOME_AIRPORT, required=False, label=_('Landing field'))
    class Meta:
        model = Flight
        
class FlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'plane', 'pilot', 'porpouse','takeoff', 'landing', 'landing_field', 'cost' )
    #list_editable = ('date', 'takeoff',  'landing', 'pilot', 'plane',)
    date_hierarchy = 'date'
    list_filter = ( 'porpouse', 'plane', 'pilot' )
    search_fields = ('id', 'pilot__sort_name', 'plane__regmark', 'plane__model', 'plane__type', 'porpouse', )
    inlines = [FlightBillInline, ]
    save_as = True
    save_on_top = True
    form = FlightAdminForm
       
admin.site.register(Flight, FlightAdmin)

class FlightBillAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'flight', 'tow_flight', 'payer', 'cost', 'cost_class',)
    list_filter = ('cost_class', 'payer',)
    search_fields = ('payer__sort_name', 'flight__id')

admin.site.register(FlightBill, FlightBillAdmin)

admin.site.register(MemberCredit)

class ReceiptDetailGenericInline(admin.TabularInline):
    model = ReceiptDetailGeneric
    fields = ('description', 'quantity', 'amount', 'total', 'memo')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'class':'note', 'rows':'1', 'cols':'30'})}
    }
    verbose_name  = 'Item'
    verbose_name_plural = 'Items'
    extra = 3
#admin.site.register(ReceiptDetailGeneric)

# class TowDetailInline(admin.TabularInline):
#     model = TowDetail
#     fields = ('cents', 'cent_cost', 'total', 'memo')
#     formfield_overrides = {
#         models.TextField: {'widget': forms.Textarea(attrs={'class':'note', 'rows':'1', 'cols':'30'})}
#     }
#     verbose_name  = 'Tow credit'
#     verbose_name_plural = 'Tow credits'
#     extra = 1
#     max_num = 1
#admin.site.register(TowDetail)


class ReceiptDetailFlightInline(admin.TabularInline):
    model = ReceiptDetailFlight
    fields = ('credit_class', 'credit', 'price_credit', 'total', 'memo')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'class':'note', 'rows':'1', 'cols':'30'})}
    }
    verbose_name  = 'Flights credit'
    verbose_name_plural = 'Flights credits'
    extra = 3
    max_num = 3




# class MotorGliderDetailInline(admin.TabularInline):
#     model = MotorGliderDetail
#     formfield_overrides = {
#         models.TextField: {'widget': forms.Textarea(attrs={'class':'note', 'rows':'1', 'cols':'30'})}
#     }
#     fields = ('cents', 'cent_cost', 'total', 'memo')
#     verbose_name  = 'Motor glider credit'
#     verbose_name_plural = 'Motor glider credits'
#     extra = 1
#     max_num = 1
#admin.site.register(MotorGliderDetail)


class ReceiptAdmin(admin.ModelAdmin):
    inlines = [ReceiptDetailGenericInline, ReceiptDetailFlightInline]   
    date_hierarchy = 'date'
    list_filter = ('description',)
    search_fields = ('reference', 'payer__sort_name', 'description')
    exclude = ('created','created_by', 'updated', 'updated_by')
    list_display = ('reference', 'date', 'payer', 'tow_cents', 'tmg_cents', 'total', 'description', 'created_by', 'created')
    #list_editable = ('reference', 'payer', 'note')
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'class':'note', 'rows':'1', 'cols':'50'})}
    }

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        else:
            obj.updated_by = request.user
        if form.is_valid():
            description = form.cleaned_data['description']
            if not description:
                if form.data:
                    cents = ugettext('Cents')
                    description = ''
                    for k,v in form.data.iteritems():
                        if 'description' in k and v:
                            description += ', '+v
                        elif 'receiptdetailflight' in k and 'credit_class' in k and v:
                            if v == 'towing':
                                cents = ugettext('Tow cents')
                            elif v == 'tmg':
                                cents = ugettext('TMG cents')
                            elif v == 'tourist':
                                cents = ugettext('Tourist cents')
                            elif v == 'promo':
                                cents = ugettext('Promotional flight')
                            description += ', '+cents
                    if description:
                        description = description[2:] 
            obj.description = description
        obj.save()



admin.site.register(Receipt, ReceiptAdmin)

class TowerLogAdmin(admin.ModelAdmin):
    list_display = ('log_file', 'created')
admin.site.register(TowerLog, TowerLogAdmin)



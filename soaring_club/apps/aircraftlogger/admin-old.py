from django.contrib import admin
from aircraftlogger.models import *

class InstallationInline(admin.TabularInline):
    model = Installation

class InstallationAdmin(admin.ModelAdmin):
    list_display = ('plane', 'flarm', 'flarmid', 'date_added', 'date_removed')    
admin.site.register(Installation, InstallationAdmin)

class OwnershipInline(admin.TabularInline):
    model = Ownership
    
class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('plane', 'pilot', 'date_purchased', 'date_sold')    
admin.site.register(Ownership, OwnershipAdmin)


class PilotAdmin(admin.ModelAdmin):
    prepopulated_fields = {'sort_name' : ('last_name', 'first_name')}
    inlines = [OwnershipInline,]
admin.site.register(Pilot, PilotAdmin)

class FlarmAdmin(admin.ModelAdmin):
    inlines = [InstallationInline,]   
admin.site.register(Flarm, FlarmAdmin)

admin.site.register(PilotCredit)
admin.site.register(ReceiptDetail)
admin.site.register(FlightBill)

class TowFlightAdmin(admin.ModelAdmin):
    list_display = ('glider', 'tow', 'payer', 'tow_duration', 'duration_unit', 'duration_rate')
    list_editable = ('glider', 'tow', 'payer', 'tow_duration', 'duration_unit', 'duration_rate')
    #date_hierarchy = 'glider.takeoff_date'
    list_filter = ('payer', 'glider',)
admin.site.register(TowFlight)

class PlaneAdmin(admin.ModelAdmin):
    list_display = ('plane_type', 'regmark', 'manufacturer', 'model')
    list_display_links = ('regmark', )
    list_filter = ('plane_type',)
    inlines = [InstallationInline, OwnershipInline]   
admin.site.register(Plane)


class TowerLogAdmin(admin.ModelAdmin):
    list_display = ('log_file', 'created')
admin.site.register(TowerLog, TowerLogAdmin)

class FlightAdmin(admin.ModelAdmin):
    list_display = ('_link', 'date', 'takeoff', 'takeoff_field', 'landing', 'landing_field', 'pilot', 'plane',)
    list_editable = ('date', 'takeoff', 'takeoff_field', 'landing', 'landing_field', 'pilot', 'plane',)
    date_hierarchy = 'date'
    list_filter = ('pilot', 'plane',)
admin.site.register(Flight, FlightAdmin)

class ReceiptDetailInline(admin.TabularInline):
    model = ReceiptDetail

class ReceiptAdmin(admin.ModelAdmin):
    inlines = [ReceiptDetailInline,]   
admin.site.register(Receipt, ReceiptAdmin)




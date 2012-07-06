from django.core.files.storage import FileSystemStorage
from django.core.exceptions import  ObjectDoesNotExist
from django.db import models
from django.contrib.auth.models import User, UserManager, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Q, permalink, signals
import django.dispatch
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.utils.functional import curry

from django.conf import settings

import os
import os.path
import time
import datetime
from debug import debug_print


# overide save for autocompilation of a field
# class User(models.Model):
#    created     = models.DateTimeField(editable=False)
#    modified    = models.DateTimeField()
#
#    def save(self, *args, **kwargs):
#        """ On save, update timestamps """
#        if not self.id:
#            self.created = datetime.datetime.today()
#        self.modified = datetime.datetime.today()
#        super(User, self).save(*args, **kwargs)
CREDIT_CLASSES = (
    ('towing', ugettext('Towing')),
    ('tmg', ugettext('Touring Motor Glider')),
    ('tourist', ugettext('Tourist propeller flight')),
    ('promo', ugettext('Promotional glider flight')),
    ('service', ugettext('Service flight')),
)

def cents_report(qfilter=None):
    report = []
    if not qfilter:
        members = Member.objects.all()
    else:
        members = Member.objects.filter(qfilter)
    for m in members:
        tc=m.tow_cents_balance()
        mc=m.tmg_cents_balance()
        if tc or mc:
            report += [{'member_id':m.id, 'first_name':m.first_name, 'last_name':m.last_name,'tow_cents':tc, 'tmg_cents':mc}]
    return report



def debits_report(qfilter=None):
    report = []
    if not qfilter:
        members = Member.objects.all()
    else:
        members = Member.objects.filter(qfilter)
    for m in members:
        debits = []
        for cls, dsc in CREDIT_CLASSES:
            d = m.balance(cls)
            debits += ((dsc, d),)
        report += [{'member_id':m.id, 'first_name':m.first_name, 'last_name':m.last_name,'debits': debits}]
    return report

def accumulate_time(begin, plus, base = datetime.datetime(1,1,1,0,0,0)):
    delta = datetime.datetime(base.year, base.month , base.day , base.hour+plus.hour , base.minute + plus.minute, base.second + plus.second ) - base
    return begin + delta

def flight_time_report(flights_from=None, flights_to=None, qfilter=None):
    '''
    Report flrght time of various type of planes.
    It's possible to specify a generic filter AND a time period filter
    '''

    report = []
    if not qfilter:
        flights = Flight.objects.all()
    else:
        flights = Flight.objects.filter(qfilter)
        
    if flights_from and flights_to:
        flights = flights.filter(Q(date__gte=flights_from) & Q(date__lte=flights_to))
            
    flight_time = {}
    n_of_flights = {}
    n_of_valid_flights = {}
    begin = datetime.datetime(1,1,1,0,0,0)
    for fl in flights:
        n_of_flights[fl.plane.type] = n_of_flights.get(fl.plane.type, 0) + 1        
        if fl.flight_duration:
            flight_time[fl.plane.type] = accumulate_time(flight_time.get(fl.plane.type, begin), fl.flight_duration)
            n_of_valid_flights[fl.plane.type] = n_of_valid_flights.get(fl.plane.type, 0) + 1
    for t, dsc in Plane.PLANE_TYPES:
        if flight_time.has_key(t):
            report += ( (dsc, n_of_flights[t], n_of_valid_flights[t], flight_time[t]-begin), )
    return report


# Create your models here.


class FlarmInstallationError(Exception):
    """
    Exception raised when the sentence is invalid
    """
    pass



class MemberType(models.Model):
    """A type of member."""

    MEMBER_TYPES = (
        ('glider_pilot', ugettext('Glider Pilot')),
        ('tmg_pilot', ugettext('TMG Pilot')),
        ('ppl_pilot', ugettext('PPL Pilot')),
        ('tow_pilot', ugettext('Tow Pilot')),
        ('student', ugettext('Student')),
        ('instructor', ugettext('Instructor')),
        ('registered', ugettext('Registered')),
        ('inactive', ugettext('Inactive')),
        ('guest', ugettext('Guest')),        
    )
    
    PILOT_TYPES = ('glider_pilot', 'tmg_pilot', 'ppl_pilot', 'tow_pilot')

    type = models.SlugField(choices=MEMBER_TYPES)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    class Meta:
        ordering = ["type"]
        verbose_name = _('Member type')
        verbose_name_plural = _('Member types')

    def __unicode__(self):
        types = dict(self.MEMBER_TYPES)
        return self.content_object.__unicode__()+' - '+types[self.type]


class Member(models.Model):
    """
    Member rappresent every person that may flight and pay for service.
    A member may also linked to a user.
    """
    user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        unique=True,
        related_name='member',
    )

    type = generic.GenericRelation(MemberType,  verbose_name=_("Type"))
    first_name = models.CharField(_("First Name"), max_length=50)
    last_name = models.CharField(_("Last Name"), max_length=50)
    sort_name = models.SlugField(_("sort name"), max_length=255)
    email = models.EmailField(_("email"), null=True, blank=True)
    notes = models.TextField(_("Notes"), null=True, blank=True)
    picture = models.ImageField(_("Picture"), null=True, blank=True, max_length=1048576, upload_to='picture/profile')
    
    @property
    def types(self):
        t = ''
        d = dict(MemberType.MEMBER_TYPES)
        for tp in self.type.values():
        
            t += d[tp['type']] + ', '
        if t:
            t = t[:-2]
        return t
        
    
    @property
    def full_name(self):
        return "%s %s" % (self.first_name, self.last_name)
    
    @property
    def membercredit_or_none(self):
        try:
            membercredit_or_none = self.membercredit
        except ObjectDoesNotExist:
            membercredit_or_none = None
        return membercredit_or_none

    def is_editable_by(self, user):
        has_membership = False
        try:
            from members.models import Membership
            has_membership = (
                Membership.objects.filter(contact=self).count() > 0
                and self.user == user
            )
        except ImportError:
            pass
        has_perms = user.has_perms((
            'member.add_profile',
            'member.change_profile',
        ))
        return (has_membership or has_perms)


    def first_receipt_date(self):
        #Check if a member has a membercredit associated. Usually membercredit
        #is created for reset member credit situation.
        if self.membercredit_or_none:
            return self.membercredit_or_none.initial_date
        else:
            receipts = self.receipt_payer.all()
            if receipts:
                return min([c.date for c in receipts])
            else:
                return datetime.date.today()            

    def first_flightbill_date(self, bills_from=None, bills_to=None):
        flightbills = self.active_flightbills(bills_from, bills_to)
        if flightbills:
            return min([fb.flight.date for fb in flightbills])
        else:
            return datetime.date.today()            

    def first_flight_date(self, flights = 'pilot', flights_from=None, flights_to=None):
        flights = self.active_flights(flights, flights_from, flights_to)
        if flights:
            return min([fb.date for fb in flights])
        else:
            return datetime.date.today()            

    def flights_missing_time_landing(self, flights = 'pilot', flights_from=None, flights_to=None):
        return self.active_flights(flights, flights_from, flights_to).filter(landing__isnull=True)

    @property
    def copilot_flights_missing_time_landing(self):
        return self.copilot.filter(landing__isnull=True)
    
    def active_receipts(self):
        '''Get receipts that occours after date of reset balance'''
        if self.membercredit_or_none:
            receipts = self.receipt_payer.filter(date__gt=self.membercredit.initial_date)
        else:
            receipts = self.receipt_payer.all()
        return receipts
    
    def active_flightbills(self, bills_from=None, bills_to=None):
        '''Get flight bills that occours after date of reset balance'''
        date = None
        #Check if a member has a membercredit associated. Usually membercredit
        #is created for reset member credit situation.
        if self.membercredit_or_none:
            date = self.membercredit.initial_date

        #Check if there is filter on date 
        if bills_from:
            #member credit has priority
            if date:
                date = max(bills_from, date)
            else:
                date = bills_from
        if date:
            #filter on selected dates
            if bills_to:
                flightbills = self.payer.filter(Q(flight__date__gte=date) & Q(flight__date__lte=bills_to))
            #filter on member credit
            else:
                flightbills = self.payer.filter(Q(flight__date__gte=date))
        #no filter
        else:
            flightbills = self.payer.all()
        return flightbills

    def active_flights(self, flights = 'pilot', flights_from=None, flights_to=None):
        '''
        Get all member flights as pilot by default.
        flights may be self.copilt for flights as copilot.
        Flights date range may also be specified.
        '''
        if flights == 'copilot':
            flights = self.copilot
        else:
            flights = self.pilot
            
        if flights_from and flights_to:
            flights_list = flights.filter(Q(date__gte=flights_from) & Q(date__lte=flights_to))
        else:
            flights_list = flights.all()
        
        return flights_list

    def active_copilot_flights(self):
        '''
        Remains for retrocompatibility and for future enanchement. 
        Simply return all flights of a member
        '''
        flights = self.copilot.all()
        return flights


    def debit(self, cost_class, bills_from=None, bills_to=None):
        '''
        debit calculated over active bills
        '''
        total_used = 0
        for fb in self.active_flightbills(bills_from, bills_to):
            if fb.cost_class == cost_class and fb.cost:        
                total_used += fb.cost
        return total_used

    def credit(self, credit_class):
        '''
        credit calculated over active receipts
        '''
        total_aquired = 0
        for c in self.active_receipts():
            total_aquired += c.flight_credit(credit_class)
        return total_aquired

    def balance(self, balance_class):
        '''balance for a certain class of cost calculated over active debits/credits'''
        return (self.credit(balance_class) - self.debit(balance_class)) 
    
    def flights_time_cumulate(flights):
        pass  
    
    def flights_durations(self, flights = 'pilot', flights_from=None, flights_to=None):
        totals = {}
        begin = datetime.datetime(1,1,1,0,0,0)
        for fl in self.active_flights(flights, flights_from, flights_to):
            if fl.flight_duration:
                totals[fl.plane.type] = accumulate_time(totals.get(fl.plane.type, begin), fl.flight_duration)
        durations = []
        for t, dsc in Plane.PLANE_TYPES:
            if totals.has_key(t):
                durations += ( (dsc, totals[t]-begin), )
        return durations

    @property
    def flights_durations_as_copilot(self):
        totals = {}
        begin = datetime.datetime(1,1,1,0,0,0)
        for fl in self.active_copilot_flights():
            if fl.flight_duration:
                totals[fl.plane.type] = accumulate_time(totals.get(fl.plane.type, begin), fl.flight_duration)
        durations = []
        for t, dsc in Plane.PLANE_TYPES:
            if totals.has_key(t):
                durations += ( (dsc, totals[t]-begin), )
        return durations


    def tow_cents_used(self):
        total_used = 0
        for fb in self.active_flightbills():
            if fb.cost_class == 'towing' and fb.cost:        
                total_used += fb.cost
        return total_used


    def tow_cents_aquired(self):
        total_aquired = 0
        for c in self.active_receipts():
            total_aquired += c.tow_cents
        return total_aquired
        
    def tow_cents_balance(self):
        return (self.tow_cents_aquired() - self.tow_cents_used()) 

    def tmg_cents_used(self):
        total_used = 0
        for fb in self.active_flightbills():
            if fb.flight.plane.type == 'tmg' and fb.cost:        
                total_used += fb.cost
        return total_used
               
    def tmg_cents_aquired(self):
        total_aquired = 0
        for c in self.active_receipts():
            if c.tmg_cents:
                total_aquired += c.tmg_cents
        return total_aquired
        
    def tmg_cents_balance(self):
        return (self.tmg_cents_aquired() - self.tmg_cents_used()) 


#     def add_accessor_methods(self, *args, **kwargs):
#         for pilot_type, name in self.PILOT_TYPES:
#             setattr(
#                 self,
#                 '%s_relations' % pilot_type,
#                 curry(self._get_TYPE_relations, pilot_type=pilot_type)
#             )
# 
#     def _get_TYPE_relations(self, pilot_type):
#         return self.pilots.filter(type=pilot_type)

#     def __init__(self, *args, **kwargs):
#         super(Pilot, self).__init__(*args, **kwargs)
#         self.add_accessor_methods()

    def __unicode__(self):
        return "%s %s" % (self.last_name, self.first_name)

    class Meta:
        ordering = ['sort_name']
        verbose_name = _('Member')
        verbose_name_plural = _('Members')
        



class Plane(models.Model):
    """
    Store plane log information
    """
    PLANE_TYPES = (
        ('glider', _('Glider')),
        ('self-launching', _('Self-launching')),
        ('tmg', _('Touring Motor Gliders')),
        ('propeller', _('Propeller')),
    )

    type = models.CharField(_("Plane Type"), max_length=32, choices=PLANE_TYPES)
    owners = models.ManyToManyField(Member, verbose_name=_("Owner"), through='Ownership')
    regmark = models.CharField(_("Registration Mark"), max_length=10)
    manufacturer = models.CharField(_("Manufacter"), max_length=50, null=True, blank=True)
    model = models.CharField(_("Model"), max_length=50, null=True, blank=True)

    def __unicode__(self):
        desc = self.regmark
        if self.model:
            desc += " " + self.model
        return desc
    class Meta:
        ordering = ['regmark']
        verbose_name = _('Plane')
        verbose_name_plural = _('Planes')
    
    @property
    def type_desc(self):
        types = dict(self.PLANE_TYPES)
        return types[self.type]

    @property
    def owners_str(self):
        owners=''
        for o in self.owners.all():
            owners += unicode(o) + ', '
        if owners:
            owners = owners[:-2]
        return owners


class Flarm(models.Model):
    serial = models.CharField(_("Serial"), default="FXXXXX", max_length=10)
    manufacturer = models.CharField(_("Manufacter"), default="Flarm", max_length=50, null=True, blank=True)
    planes = models.ManyToManyField(Plane,  verbose_name=_("Plane"), through='Installation')
    def __unicode__(self):
        desc = self.serial
        if self.manufacturer:
            desc += " " + self.manufacturer
        return desc


class Installation(models.Model):
    plane = models.ForeignKey(Plane, verbose_name=_("Plane"))
    flarm = models.ForeignKey(Flarm, verbose_name=_("Flarm"))
    flarmid = models.CharField(_("Flarm ID"), default="", max_length=10)
    date_added = models.DateTimeField(verbose_name=_("Installation date"))
    date_removed = models.DateTimeField(null=True, blank=True, verbose_name=_("Change/Removed date"))
    def __unicode__(self):
        desc = "Installed flarm %s, identified by %s,  on %s aircraft %s" % (self.flarm.serial, self.flarmid, self.date_added, self.plane.regmark)
        if self.date_removed:
            desc = desc + " removed on %s" % self.date_removed
        return desc
    @classmethod
    def get_flarm_by_date(cls, flarmid, date):
        flarms = cls.objects.filter(Q(flarmid__iexact=flarmid),
                                    Q(date_added__lte=date),
                                    Q(date_removed__gte=date) | Q(date_removed__isnull=True) )
        if len(flarms) > 1:
            raise FlarmInstallationError("Installation database inconsistence for flarm with id=%s" % (flarmid,) )
        if flarms:
            return flarms[0]
        else:
            return None

    class Meta:
        ordering = ['-date_added']
        verbose_name = _('Installation')
        verbose_name_plural = _('Installations')


class Ownership(models.Model):
    plane = models.ForeignKey(Plane)
    owner = models.ForeignKey(Member)
    date_purchased = models.DateField(verbose_name=_("Purchase date"))
    date_sold = models.DateField(null=True, blank=True, verbose_name=_("Date of sale"))
    def __unicode__(self):
        desc = "Member %s purchased aircraft %s on %s" % (self.owner.__unicode__(), self.plane.regmark, self.date_purchased)
        return desc
    class Meta:
        ordering = ['-date_purchased']
        verbose_name = _('Ownership')
        verbose_name_plural = _('Ownerships')

class Flight(models.Model):
    date = models.DateField(_('Date'))
    takeoff = models.TimeField(_('Takeoff'), null=True, blank=True)
    takeoff_field = models.CharField(_('Takeoff field'), default="", max_length=20, null=True, blank=True)
    landing = models.TimeField(_('Landing'), null=True, blank=True)
    landing_field = models.CharField(_('Landing field'), default="", max_length=20, null=True, blank=True)
    pilot = models.ForeignKey(Member, verbose_name=_("Pilot"), limit_choices_to = ~Q(type__type__exact='inactive') , related_name='pilot', null=True, blank=True)
    copilot = models.ForeignKey(Member,  verbose_name=_("Instructor"), limit_choices_to = Q(type__type__exact='instructor') & ~Q(type__type__exact='inactive'), related_name='copilot', null=True, blank=True)
    plane = models.ForeignKey(Plane,  verbose_name=_("Plane"), null=True, blank=True)
    porpouse = models.CharField(_("Porpouse"), default="", max_length=50, null=True, blank=True)
    
    @property
    def flight_duration(self):
        if self.landing and self.takeoff:
            landing = self.landing.hour*3600+self.landing.minute*60+self.landing.second
            takeoff = self.takeoff.hour*3600+self.takeoff.minute*60+self.takeoff.second
            if landing > takeoff:
                delta = landing - takeoff
                hour = delta // 3600
                minute = (delta - hour*3600) // 60
                second = (delta - hour*3600 - minute*60)
                return datetime.time(hour, minute, second)
        else:
            return datetime.time(0, 0, 0)
            
    @property
    def cost(self):
        if self.flight:
            return self.flight.cost
        else:
            return 0

    class Meta:
        ordering = ['-id', '-date',]
        verbose_name = _('Flight')
        verbose_name_plural = _('Flights')

    def __unicode__(self):
        if self.takeoff:
            return "%s-%s-%s" % (self.date.strftime(settings.DATE_FORMAT_STRF), self.takeoff.strftime(settings.TIME_FORMAT_STRF), self.plane.regmark  )
        else:
            return "%s-%s" % (self.date.strftime(settings.DATE_FORMAT_STRF), self.plane.regmark  )
        

    @permalink
    def get_absolute_url(self):
        return ('flight_update', None, {'object_id':str(self.pk)})

    @permalink
    def get_delete_url(self):
        return ('flight_delete', None, {'object_id':str(self.pk)})

# class FlightTable(models.Model):
#     date = models.DateField(_('Date'))
#     tow_plane = models.ForeignKey(Plane, null=True, blank=True,limit_choices_to = Q(plane__type__exact='propeller')) 
#     tow_pilot = models.ForeignKey(Member, limit_choices_to = Q(type__type__in=('tow_pilot',)))
#     hours_counter_init = models.DecimalField(_('Initial Hours Counter'), max_digits=10, decimal_places=2, null=True, blank=True)
#     hours_counter_warmup = models.DecimalField(_('Warmup Hours Counter'), max_digits=10, decimal_places=2, null=True, blank=True)
#     counter_unit = models.DecimalField(_('Counter unit'), max_digits=3, decimal_places=0,
#                                         default=100,
#                                         choices=FlightBill.DURATION_UNITS, null=True, blank=True)      
# 
# 
# 

class ReceiptManager(models.Manager):
    def user_total(self, user_id):
        qs = self.filter(payer__id = user_id)
        total = 0
        for q in qs:
            total += q.total
        return total


    def user_total_tow_cents(self, user_id):
        qs = self.filter(payer__id = user_id)
        total = 0
        for q in qs:
            total += q.tow_cents
        return total

    def user_total_tmg_cents(self, user_id):
        qs = self.filter(payer__id = user_id)
        total = 0
        for q in qs:
            total += q.tmg_cents
        return total

    def user_first_date(self, user_id):
        qs = self.filter(payer__id = user_id)
        return min([q.date for q in qs])
        
class Receipt(models.Model):
    reference = models.CharField(_('Reference'),max_length=20)
    date = models.DateField(_('Date'))
    payer = models.ForeignKey(Member,
                              limit_choices_to = ~Q(type__type__exact='inactive'),
                              related_name='receipt_payer', 
                              null=True, blank=True,
                              verbose_name=_('Payer')
                              )
    description = models.CharField(_('Description of payment'), max_length=255, null=True, blank=True)
    created = models.DateTimeField(_('Created in'))
    updated = models.DateTimeField(_('Updated in'),null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        related_name='created_receipts',
        verbose_name=_("Created by"),
    )
    updated_by = models.ForeignKey(
        User,
        related_name='updated_receipts',
        verbose_name=_("Updated by"),
        null=True, blank=True,
    )

    note = models.TextField(_('Note'), null=True, blank=True)
    objects = ReceiptManager()
    
    def save(self):
        if not self.id:
            self.created = datetime.datetime.today()
        self.updated = datetime.datetime.today()
        super(Receipt, self).save()

    @property
    def total(self):
        t = 0
        for cls, desc in CREDIT_CLASSES:
            t += self.flight_total(cls)
        return round(self.generic_total + t, 2)

    @property
    def generic_total(self):
        total = 0
        for item in self.receiptdetailgeneric_set.all():
            total += item.total
        return total

    def flight_total(self, credit_class):
        total = 0
        for item in self.receiptdetailflight_set.filter(credit_class__exact=credit_class):
            if item.total:
                total += item.total
        return total

    def flight_credit(self, credit_class):
        total = 0
        for item in self.receiptdetailflight_set.filter(credit_class__exact=credit_class):
            if item.credit:
                total += item.credit
        return total

    @property
    def credits(self):
        c = []
        for cls, desc in CREDIT_CLASSES:
            c += ((desc, self.flight_credit(cls)),)
        return c

    @property
    def tow_price(self):
        return self.flight_total('towing')

    @property
    def tow_cents(self):
        return self.flight_credit('towing')


    @property
    def tmg_price(self):
        return self.flight_total('tmg')

    @property
    def tmg_cents(self):
        return self.flight_credit('tmg')

#     objects = ReceiptManager()
    def __unicode__(self):
        return "(%s - %s:%s) - %s - %s" % (self.date,
                                           self.created_by,
                                           self.reference,
                                           self.payer,
                                           self.total)
    class Meta:
        ordering = ['-date', '-reference']
        verbose_name = _('Receipt')
        verbose_name_plural = _('Receipts')




class ReceiptDetail(models.Model):
    """
    Abstract class for details of a receipt
    """
    receipt = models.ForeignKey(Receipt, verbose_name=_("Invoice"))
    memo = models.TextField(_("Notes"), null=True, blank=True)
    total = models.DecimalField(_("Total Price"), max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-receipt__created', '-receipt__reference']
        abstract = True


class ReceiptDetailGeneric(ReceiptDetail):
    """
    Generic detail of a receipt.
    Only amount must be entered.
    If quantity is not entered it is set to 1.
    Total is dervided from quantity and amount.
    """
    description = models.CharField(_("Description"), max_length=100)
    quantity = models.IntegerField(_("Quantity"), blank=True)
    amount = models.DecimalField(_("Unit Price"), max_digits=10, decimal_places=2)

    def save(self):
        if not self.quantity:
            self.quantity = 1
        self.total = self.amount * self.quantity
        super(ReceiptDetailGeneric, self).save()

    def __unicode__(self):
        return "(%s:%s - %s) %s: %s %s eur" % (self.receipt.date,
                                            self.receipt.created_by,
                                            self.receipt.reference,
                                            self.receipt.payer,
                                            self.description,
                                            self.total,
                                           )

    class Meta:
        verbose_name = _('Receipt generic detail')
        verbose_name_plural = _('Receipt generics details')


class ReceiptDetailFlight(ReceiptDetail):
    credit = models.DecimalField(_("Credit"), blank=True, max_digits=10, decimal_places=2)
    price_credit = models.DecimalField(_("Price/credit unit"), blank=True, default=settings.DURATION_TOW_RATE, max_digits=10, decimal_places=2)
    credit_class = models.CharField(_("Credit class"), blank=True, max_length=32, choices=CREDIT_CLASSES)

    def save(self):
        if self.total and self.price_credit:
            self.credit = self.total / self.price_credit
        elif self.credit and self.price_credit:
            self.total = self.credit * self.price_credit
        elif self.credit and self.total:
            self.price_credit = self.total / self.credit
            
        super(ReceiptDetailFlight, self).save()

    def __unicode__(self):
        return "(%s:%s - %s) %s %s %s cents %s eur" % (self.receipt.date,
                                                  self.receipt.created_by,
                                                  self.receipt.reference,
                                                  self.receipt.payer,
                                                  self.credit_class,
                                                  self.credit,
                                                  self.total,
                                                 )
    class Meta:
        verbose_name = _('Flight receipt detail')
        verbose_name_plural = _('Flights receipt details')



class FlightBillManager(models.Manager):

    def payer_total_tow_cents(self, user_id):
        qs = self.filter(payer__id = user_id)
        total = 0
        for q in qs:
            if q.class_cost == 'towing' and q.cost:
                total += q.cost
        return total

    def payer_total_tmg_cents(self, user_id):
        qs = self.filter(payer__id = user_id)
        total = 0
        for q in qs:
            if q.class_cost == 'tmg' and q.cost:        
                total += q.cost
        return total

    def payer_first_date(self, user_id):
        qs = self.filter(payer__id = user_id)
        return min([q.flight.date for q in qs])


class FlightBill(models.Model):
    flight = models.OneToOneField(Flight, 
                                  related_name='flight', 
                                  verbose_name = _('Flight')
                                  )
    tow_flight = models.OneToOneField(Flight, 
                                      related_name='tow_flight', 
                                      verbose_name = _('Tow Flight'),
                                      limit_choices_to = Q(plane__type__exact='glider') | Q(plane__type__exact='self-launching'), 
                                      null=True, blank=True) 
    payer = models.ForeignKey(Member,  
                              limit_choices_to = ~Q(type__type__exact='inactive'), 
                              related_name='payer', 
                              verbose_name = _('Payer'),
                              null=True, blank=True)
    cost = models.DecimalField(_("Flight cost"), 
                                      max_digits=4, 
                                      decimal_places=0, 
                                      null=True, blank=True)

    cost_class =  models.CharField(_("Cost class"), 
                                   max_length=32, 
                                   choices=CREDIT_CLASSES, 
                                   null=True, blank=True)


    objects = FlightBillManager()
    class Meta:
        verbose_name = _('Flight Bill')
        verbose_name_plural = _('Flights Bills')
        ordering = ['flight']
    
    @property
    def class_desc(self):
        classes = dict(CREDIT_CLASSES)
        return classes[self.cost_class]

    def __unicode__(self):
        cost = cost_class = takeoff = ''
        if self.cost:
            cost = self.cost
        if self.cost_class:
            cost_class = self.cost_class
        if self.flight.takeoff:
            takeoff = self.flight.takeoff.strftime(settings.TIME_FORMAT_STRF)
        return "%s-%s %s %s" % (self.flight.date.strftime(settings.DATE_FORMAT_STRF),
                                takeoff,
                                cost,
                                cost_class)

class MemberCredit(models.Model):
    member = models.OneToOneField(Member, verbose_name = _('Member'))
    initial_date = models.DateField(_('Initial date'))
    tow_initial_credit = models.DecimalField(_('Initial tow credit'), max_digits=10, decimal_places=2, default=0)
    motorglider_initial_credit = models.DecimalField(_('Initial TMG credit'), max_digits=10, decimal_places=2, default=0)
    def __unicode__(self):
        return u"%s %s: tow cents=%s  tmg cents=%s" % (self.member, 
                                                       self.initial_date, 
                                                       self.tow_initial_credit, 
                                                       self.motorglider_initial_credit,
                                                      )

    class Meta:
        ordering = ['member']
        verbose_name = _('Member credit')
        verbose_name_plural = _('Member credits')


log_file_storage = FileSystemStorage(location=os.path.join(os.path.dirname(__file__),'media'), base_url='/media/')
class TowerLog(models.Model):
    log_file = models.FileField(storage=log_file_storage, upload_to='rec')
    created = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True, auto_now_add=True, editable=False)
    def __unicode__(self):
        return self.created.isoformat()
    class Meta:
        ordering = ['-created']


def install():
    group, created = Group.objects.get_or_create(name=settings.ADMIN_GROUP)
    if created:
        perms = Permission.objects.filter(
            content_type__in=ContentType.objects.filter(app_label='aircraftlogger')
        )
        for perm in perms:
            group.permissions.add(perm)


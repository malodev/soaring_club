# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MemberType'
        db.create_table('aircraftlogger_membertype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('aircraftlogger', ['MemberType'])

        # Adding model 'Member'
        db.create_table('aircraftlogger_member', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='member', unique=True, null=True, to=orm['auth.User'])),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sort_name', self.gf('django.db.models.fields.SlugField')(max_length=255)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, null=True, blank=True)),
            ('notes', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('picture', self.gf('django.db.models.fields.files.ImageField')(max_length=1048576, null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['Member'])

        # Adding model 'Plane'
        db.create_table('aircraftlogger_plane', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=32)),
            ('regmark', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('manufacturer', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['Plane'])

        # Adding model 'Flarm'
        db.create_table('aircraftlogger_flarm', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('serial', self.gf('django.db.models.fields.CharField')(default='FXXXXX', max_length=10)),
            ('manufacturer', self.gf('django.db.models.fields.CharField')(default='Flarm', max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['Flarm'])

        # Adding model 'Installation'
        db.create_table('aircraftlogger_installation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plane', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aircraftlogger.Plane'])),
            ('flarm', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aircraftlogger.Flarm'])),
            ('flarmid', self.gf('django.db.models.fields.CharField')(default='', max_length=10)),
            ('date_added', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_removed', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['Installation'])

        # Adding model 'Ownership'
        db.create_table('aircraftlogger_ownership', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plane', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aircraftlogger.Plane'])),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aircraftlogger.Member'])),
            ('date_purchased', self.gf('django.db.models.fields.DateField')()),
            ('date_sold', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['Ownership'])

        # Adding model 'Flight'
        db.create_table('aircraftlogger_flight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('takeoff', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('takeoff_field', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, blank=True)),
            ('landing', self.gf('django.db.models.fields.TimeField')(null=True, blank=True)),
            ('landing_field', self.gf('django.db.models.fields.CharField')(default='', max_length=20, null=True, blank=True)),
            ('pilot', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='pilot', null=True, to=orm['aircraftlogger.Member'])),
            ('copilot', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='copilot', null=True, to=orm['aircraftlogger.Member'])),
            ('plane', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aircraftlogger.Plane'], null=True, blank=True)),
            ('porpouse', self.gf('django.db.models.fields.CharField')(default='', max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['Flight'])

        # Adding model 'Receipt'
        db.create_table('aircraftlogger_receipt', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('date', self.gf('django.db.models.fields.DateField')()),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='receipt_payer', null=True, to=orm['aircraftlogger.Member'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created_receipts', to=orm['auth.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='updated_receipts', null=True, to=orm['auth.User'])),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['Receipt'])

        # Adding model 'ReceiptDetailGeneric'
        db.create_table('aircraftlogger_receiptdetailgeneric', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('receipt', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aircraftlogger.Receipt'])),
            ('memo', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('total', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('quantity', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal('aircraftlogger', ['ReceiptDetailGeneric'])

        # Adding model 'ReceiptDetailFlight'
        db.create_table('aircraftlogger_receiptdetailflight', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('receipt', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['aircraftlogger.Receipt'])),
            ('memo', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('total', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=10, decimal_places=2, blank=True)),
            ('credit', self.gf('django.db.models.fields.DecimalField')(max_digits=10, decimal_places=2, blank=True)),
            ('price_credit', self.gf('django.db.models.fields.DecimalField')(default=2.5, max_digits=10, decimal_places=2, blank=True)),
            ('credit_class', self.gf('django.db.models.fields.CharField')(max_length=32, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['ReceiptDetailFlight'])

        # Adding model 'FlightBill'
        db.create_table('aircraftlogger_flightbill', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('flight', self.gf('django.db.models.fields.related.OneToOneField')(related_name='flight', unique=True, to=orm['aircraftlogger.Flight'])),
            ('tow_flight', self.gf('django.db.models.fields.related.OneToOneField')(blank=True, related_name='tow_flight', unique=True, null=True, to=orm['aircraftlogger.Flight'])),
            ('payer', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='payer', null=True, to=orm['aircraftlogger.Member'])),
            ('cost', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=4, decimal_places=0, blank=True)),
            ('cost_class', self.gf('django.db.models.fields.CharField')(max_length=32, null=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['FlightBill'])

        # Adding model 'MemberCredit'
        db.create_table('aircraftlogger_membercredit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('member', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['aircraftlogger.Member'], unique=True)),
            ('initial_date', self.gf('django.db.models.fields.DateField')()),
            ('tow_initial_credit', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
            ('motorglider_initial_credit', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=10, decimal_places=2)),
        ))
        db.send_create_signal('aircraftlogger', ['MemberCredit'])

        # Adding model 'TowerLog'
        db.create_table('aircraftlogger_towerlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('log_file', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('aircraftlogger', ['TowerLog'])


    def backwards(self, orm):
        # Deleting model 'MemberType'
        db.delete_table('aircraftlogger_membertype')

        # Deleting model 'Member'
        db.delete_table('aircraftlogger_member')

        # Deleting model 'Plane'
        db.delete_table('aircraftlogger_plane')

        # Deleting model 'Flarm'
        db.delete_table('aircraftlogger_flarm')

        # Deleting model 'Installation'
        db.delete_table('aircraftlogger_installation')

        # Deleting model 'Ownership'
        db.delete_table('aircraftlogger_ownership')

        # Deleting model 'Flight'
        db.delete_table('aircraftlogger_flight')

        # Deleting model 'Receipt'
        db.delete_table('aircraftlogger_receipt')

        # Deleting model 'ReceiptDetailGeneric'
        db.delete_table('aircraftlogger_receiptdetailgeneric')

        # Deleting model 'ReceiptDetailFlight'
        db.delete_table('aircraftlogger_receiptdetailflight')

        # Deleting model 'FlightBill'
        db.delete_table('aircraftlogger_flightbill')

        # Deleting model 'MemberCredit'
        db.delete_table('aircraftlogger_membercredit')

        # Deleting model 'TowerLog'
        db.delete_table('aircraftlogger_towerlog')


    models = {
        'aircraftlogger.flarm': {
            'Meta': {'object_name': 'Flarm'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'default': "'Flarm'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'planes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['aircraftlogger.Plane']", 'through': "orm['aircraftlogger.Installation']", 'symmetrical': 'False'}),
            'serial': ('django.db.models.fields.CharField', [], {'default': "'FXXXXX'", 'max_length': '10'})
        },
        'aircraftlogger.flight': {
            'Meta': {'ordering': "['-id', '-date']", 'object_name': 'Flight'},
            'copilot': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'copilot'", 'null': 'True', 'to': "orm['aircraftlogger.Member']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'landing': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'landing_field': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'pilot': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'pilot'", 'null': 'True', 'to': "orm['aircraftlogger.Member']"}),
            'plane': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aircraftlogger.Plane']", 'null': 'True', 'blank': 'True'}),
            'porpouse': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'takeoff': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'takeoff_field': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'null': 'True', 'blank': 'True'})
        },
        'aircraftlogger.flightbill': {
            'Meta': {'ordering': "['flight']", 'object_name': 'FlightBill'},
            'cost': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '4', 'decimal_places': '0', 'blank': 'True'}),
            'cost_class': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'flight': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'flight'", 'unique': 'True', 'to': "orm['aircraftlogger.Flight']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'payer'", 'null': 'True', 'to': "orm['aircraftlogger.Member']"}),
            'tow_flight': ('django.db.models.fields.related.OneToOneField', [], {'blank': 'True', 'related_name': "'tow_flight'", 'unique': 'True', 'null': 'True', 'to': "orm['aircraftlogger.Flight']"})
        },
        'aircraftlogger.installation': {
            'Meta': {'ordering': "['-date_added']", 'object_name': 'Installation'},
            'date_added': ('django.db.models.fields.DateTimeField', [], {}),
            'date_removed': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'flarm': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aircraftlogger.Flarm']"}),
            'flarmid': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plane': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aircraftlogger.Plane']"})
        },
        'aircraftlogger.member': {
            'Meta': {'ordering': "['sort_name']", 'object_name': 'Member'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'picture': ('django.db.models.fields.files.ImageField', [], {'max_length': '1048576', 'null': 'True', 'blank': 'True'}),
            'sort_name': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'member'", 'unique': 'True', 'null': 'True', 'to': "orm['auth.User']"})
        },
        'aircraftlogger.membercredit': {
            'Meta': {'ordering': "['member']", 'object_name': 'MemberCredit'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_date': ('django.db.models.fields.DateField', [], {}),
            'member': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['aircraftlogger.Member']", 'unique': 'True'}),
            'motorglider_initial_credit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'tow_initial_credit': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'})
        },
        'aircraftlogger.membertype': {
            'Meta': {'ordering': "['type']", 'object_name': 'MemberType'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'type': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'aircraftlogger.ownership': {
            'Meta': {'ordering': "['-date_purchased']", 'object_name': 'Ownership'},
            'date_purchased': ('django.db.models.fields.DateField', [], {}),
            'date_sold': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aircraftlogger.Member']"}),
            'plane': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aircraftlogger.Plane']"})
        },
        'aircraftlogger.plane': {
            'Meta': {'ordering': "['regmark']", 'object_name': 'Plane'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manufacturer': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'owners': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['aircraftlogger.Member']", 'through': "orm['aircraftlogger.Ownership']", 'symmetrical': 'False'}),
            'regmark': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'aircraftlogger.receipt': {
            'Meta': {'ordering': "['-date', '-reference']", 'object_name': 'Receipt'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_receipts'", 'to': "orm['auth.User']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'payer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'receipt_payer'", 'null': 'True', 'to': "orm['aircraftlogger.Member']"}),
            'reference': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'updated_receipts'", 'null': 'True', 'to': "orm['auth.User']"})
        },
        'aircraftlogger.receiptdetailflight': {
            'Meta': {'object_name': 'ReceiptDetailFlight'},
            'credit': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'credit_class': ('django.db.models.fields.CharField', [], {'max_length': '32', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memo': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'price_credit': ('django.db.models.fields.DecimalField', [], {'default': '2.5', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'receipt': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aircraftlogger.Receipt']"}),
            'total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        'aircraftlogger.receiptdetailgeneric': {
            'Meta': {'object_name': 'ReceiptDetailGeneric'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'memo': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'receipt': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['aircraftlogger.Receipt']"}),
            'total': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'})
        },
        'aircraftlogger.towerlog': {
            'Meta': {'ordering': "['-created']", 'object_name': 'TowerLog'},
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['aircraftlogger']
from django.db import models
from django.utils import timezone
# Create your models here.
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.relpath(__file__)))


class Inference(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.IntegerField(null=True, blank=True)
    inference_label = models.IntegerField(default=0)
    inference_text = models.TextField(blank=True, max_length=200)
    inference_results = models.CharField(max_length=100, blank=True,)

class Data(models.Model):
    id = models.CharField(max_length=1000, primary_key=True)
    filename = models.CharField(max_length=100)
    filepath = models.ImageField(max_length=255, upload_to=os.path.join(BASE_DIR,'media/data'), default=None, blank=True)

class DataAPI(models.Model):
    
    id = models.AutoField(primary_key=True, null=False, default=None)
    customer_id  = models.IntegerField(null=True, default=None)
    admin_id  = models.IntegerField(null=False, default=None)
    deliverer_id = models.IntegerField(null=True, default=None)
    returned_items = models.IntegerField(null=False, default=0)
    discount  = models.IntegerField(null=False, default=0)
    refund  = models.IntegerField(null=False, default=0)
    total = models.IntegerField(null=False, default=0)
    items_count = models.IntegerField(null=False, default=0)
    destination = models.CharField(max_length=255, default=None, null=False)
    contact = models.CharField(max_length=255, null=True)
    has_discount = models.IntegerField(null=True, default=0)
    is_poked = models.IntegerField(null=False, default=0)
    receipt = models.CharField(max_length=255, null=True, default=None)
    amount = models.IntegerField(null=False, default=None)
    total_buying_price = models.IntegerField(null=False, default=0)
    is_paid = models.IntegerField(null=False, default=None)
    transaction_id = models.IntegerField(null=True, default=None)
    selcom_order = models.CharField(max_length=255, null=True, default=None)
    invoice_number = models.CharField(max_length=255, null=True, default=None)
    paid_at = models.DateTimeField(null=False, default=None)
    is_processed = models.IntegerField(null=False, default=None)
    is_informed = models.IntegerField(null=False, default=0)
    notification_count = models.IntegerField(null=False, default=0)
    status = models.CharField(max_length=255, null=False, default='Unpaid')
    is_received = models.IntegerField(null=False, default=0)
    processed_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    tagname = models.CharField(max_length=255, null=True, default=None)
    created_at = models.DateTimeField(null=True, default=None)
    updated_at = models.DateTimeField(null=True, default=None)


from django.contrib import admin
from .models import Customer, Order, RfmSegment


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'customer_name', 'segment')
    search_fields = ('customer_id', 'customer_name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'customer', 'order_date', 'category', 'sales', 'profit')
    list_filter = ('category', 'region', 'order_date')
    search_fields = ('order_id',)


@admin.register(RfmSegment)
class RfmSegmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'segment', 'recency', 'frequency', 'monetary')
    list_filter = ('segment',)

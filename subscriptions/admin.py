# subscriptions/admin.py

from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, Purchase

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_id_apple', 'product_id_google', 'duration_days', 'is_active')

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'plan')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'store', 'purchase_date', 'is_verified')
    list_filter = ('store', 'is_verified', 'purchase_date')
    search_fields = ('user__username', 'transaction_id')
    raw_id_fields = ('user', 'plan')
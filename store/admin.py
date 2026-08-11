from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Address, ServiceablePincode, StoreSettings, Category, Product,
    Inventory, ProductBundle, BundleItem, Order, OrderItem, Coupon,
    Review, Invoice, Refund, PaymentWebhookEvent, AuditLog, Consent, BulkImportJob
)

# Custom User Admin to handle extended fields
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "phone", "is_staff")
    list_filter = ("role", "is_staff", "is_superuser")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("role", "phone")}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("user", "line1", "pincode", "is_default")
    search_fields = ("pincode", "line1", "user__username")

@admin.register(ServiceablePincode)
class ServiceablePincodeAdmin(admin.ModelAdmin):
    list_display = ("pincode", "instant_eligible", "scheduled_eligible", "estimated_instant_minutes")
    list_filter = ("instant_eligible", "scheduled_eligible")

@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = ("open_time", "close_time", "instant_cutoff_time")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent_category")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "brand", "price", "discounted_price")
    list_filter = ("category", "brand")
    search_fields = ("name", "brand")

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "available_quantity")
    search_fields = ("product__name",)

class BundleItemInline(admin.TabularInline):
    model = BundleItem
    extra = 1

@admin.register(ProductBundle)
class ProductBundleAdmin(admin.ModelAdmin):
    list_display = ("name", "bundle_price")
    inlines = [BundleItemInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price_at_purchase", "fulfillment_status")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order_status", "payment_status", "delivery_mode", "total", "created_at")
    list_filter = ("order_status", "payment_status", "delivery_mode")
    search_fields = ("id", "user__username")
    inlines = [OrderItemInline]

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_type", "discount_value", "valid_from", "valid_to")
    search_fields = ("code",)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating",)

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "order", "gstin", "gst_amount", "issued_at")
    search_fields = ("invoice_number", "order__id")

@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "status", "razorpay_refund_id", "created_at")
    list_filter = ("status",)

@admin.register(PaymentWebhookEvent)
class PaymentWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("razorpay_event_id", "event_type", "processed_at")
    search_fields = ("razorpay_event_id", "event_type")

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "entity_type", "entity_id", "user", "created_at")
    list_filter = ("action", "entity_type")

@admin.register(Consent)
class ConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "consent_type", "policy_version", "accepted_at")
    list_filter = ("consent_type",)

@admin.register(BulkImportJob)
class BulkImportJobAdmin(admin.ModelAdmin):
    list_display = ("id", "admin_user", "status", "success_count", "error_count", "created_at")
    list_filter = ("status",)
from django.db import models
from django.contrib.auth.models import AbstractUser

# In store/models.py
from django.db import models
from django.conf import settings

class RefundRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Refund Processed'),
    ]

    REASON_CHOICES = [
        ('damaged', 'Damaged / Expired Item'),
        ('missing', 'Missing Item in Delivery'),
        ('wrong_item', 'Wrong Item Delivered'),
        ('quality', 'Quality Not Satisfactory'),
        ('other', 'Other Reason'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='refund_requests')
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='refund_requests')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES, default='damaged')
    description = models.TextField(help_text="Detailed reason for refund")
    
    # 👈 Proof image or video upload
    proof_file = models.FileField(upload_to='refund_proofs/', null=True, blank=True, help_text="Upload image/video proof")
    
    amount_requested = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Refund #{self.id} for Order #{self.order.id} — {self.get_status_display()}"


# ---------- Users & Addresses ----------

class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        EMPLOYEE = "employee", "Employee"
        MANAGER = "manager", "Manager"
        ADMIN = "admin", "Admin"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    pincode = models.CharField(max_length=10)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, default="Mumbai")
    state = models.CharField(max_length=100, default="Maharashtra")
    is_default = models.BooleanField(default=False)

    def street_address(self):
        """Returns readable street lines."""
        if self.line2:
            return f"{self.line1}, {self.line2}"
        return self.line1

    def __str__(self):
        return f"{self.line1}, {self.pincode}"


class ServiceablePincode(models.Model):
    pincode = models.CharField(max_length=10, primary_key=True)
    instant_eligible = models.BooleanField(default=True)
    scheduled_eligible = models.BooleanField(default=False)
    estimated_instant_minutes = models.IntegerField(default=30)

    def __str__(self):
        return self.pincode


# ---------- Store Config ----------

class StoreSettings(models.Model):
    open_time = models.CharField(max_length=5, default="09:00")
    close_time = models.CharField(max_length=5, default="22:00")
    instant_cutoff_time = models.CharField(max_length=5, default="21:45")

    def __str__(self):
        return f"Store hours {self.open_time}-{self.close_time} (instant cutoff {self.instant_cutoff_time})"

    class Meta:
        verbose_name = "Store Settings"
        verbose_name_plural = "Store Settings"


# ---------- Catalog & Inventory ----------

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey(
        "self", on_delete=models.SET_NULL, blank=True, null=True, related_name="children"
    )
    # Dual Image Handling for Categories
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    def get_image(self):
        """Returns local uploaded image URL or external URL."""
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/150"

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, blank=True, null=True)
    unit = models.CharField(max_length=50)  # e.g., '500g', '1 L', '1 Pack'
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    # Dual Image Handling
    image = models.ImageField(upload_to='products/', blank=True, null=True)  # Local File Upload
    image_url = models.URLField(blank=True, null=True)                      # External URL
    
    description = models.TextField(blank=True, null=True)
    dietary_tags = models.JSONField(default=list, blank=True)

    def get_final_price(self):
        """Returns discounted price if present, else original price."""
        if self.discounted_price:
            return self.discounted_price
        return self.price

    def get_image(self):
        """Helper method to return uploaded file URL or external image URL."""
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return "https://via.placeholder.com/300"

    def __str__(self):
        return self.name


class Inventory(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, related_name="inventory")
    available_quantity = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product.name}: {self.available_quantity}"

    class Meta:
        verbose_name_plural = "Inventory"


class ProductBundle(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    bundle_price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name


class BundleItem(models.Model):
    bundle = models.ForeignKey(ProductBundle, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.bundle.name}"


# ---------- Orders & Checkout ----------

class Order(models.Model):
    class DeliveryMode(models.TextChoices):
        INSTANT = "instant", "Instant Delivery (30 Mins)"

    class OrderStatus(models.TextChoices):
        PENDING_ACCEPTANCE = "pending_acceptance", "Pending Acceptance"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        PREPARING = "preparing", "Preparing"
        PACKED = "packed", "Packed"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    class PickingStatus(models.TextChoices):
        UNPICKED = "unpicked", "Unpicked"
        PICKING = "picking", "Picking"
        PICKED = "picked", "Picked"
        PACKED = "packed", "Packed"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"
        PARTIALLY_REFUNDED = "partially_refunded", "Partially Refunded"

    class PaymentMethod(models.TextChoices):
        COD = "COD", "Cash on Delivery"
        UPI = "UPI", "UPI / Online"

    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="orders")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders")
    
    # Strictly Instant 30-min Delivery
    delivery_mode = models.CharField(
        max_length=20,
        choices=DeliveryMode.choices,
        default=DeliveryMode.INSTANT
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD
    )
    scheduled_slot_start = models.DateTimeField(blank=True, null=True)
    scheduled_slot_end = models.DateTimeField(blank=True, null=True)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    order_status = models.CharField(
        max_length=25, choices=OrderStatus.choices, default=OrderStatus.PENDING_ACCEPTANCE
    )
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)
    
    # Internal order tracking
    accepted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="accepted_orders"
    )
    accepted_at = models.DateTimeField(blank=True, null=True)
    picking_status = models.CharField(
        max_length=20, choices=PickingStatus.choices, default=PickingStatus.UNPICKED
    )
    delivery_instructions = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} — {self.user.username} ({self.order_status})"


class OrderItem(models.Model):
    class FulfillmentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PICKED = "picked", "Picked"
        OUT_OF_STOCK = "out_of_stock", "Out of Stock"
        SUBSTITUTED = "substituted", "Substituted"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    fulfillment_status = models.CharField(
        max_length=20, choices=FulfillmentStatus.choices, default=FulfillmentStatus.PENDING
    )
    substituted_product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True, related_name="substituted_in_items"
    )

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        FLAT = "flat", "Flat"
        PERCENTAGE = "percentage", "Percentage"

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    def __str__(self):
        return self.code


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating}★ — {self.product.name}"


# ---------- Compliance & Production ----------

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="invoice")
    invoice_number = models.CharField(max_length=50, unique=True)
    gstin = models.CharField(max_length=20)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_pdf_url = models.URLField(blank=True, null=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.invoice_number


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="refunds")
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.SET_NULL, blank=True, null=True, related_name="refunds"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    razorpay_refund_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund ₹{self.amount} — Order #{self.order_id}"


class PaymentWebhookEvent(models.Model):
    razorpay_event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.event_type} ({self.razorpay_event_id})"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="audit_entries")
    action = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=50)
    field_changed = models.CharField(max_length=100, blank=True, null=True)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.entity_type}#{self.entity_id} by {self.user}"

    class Meta:
        verbose_name = "Audit Log Entry"


class Consent(models.Model):
    class ConsentType(models.TextChoices):
        PRIVACY_POLICY = "privacy_policy", "Privacy Policy"
        MARKETING_EMAIL = "marketing_email", "Marketing Email"
        TERMS_OF_SERVICE = "terms_of_service", "Terms of Service"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="consents")
    consent_type = models.CharField(max_length=30, choices=ConsentType.choices)
    accepted_at = models.DateTimeField(auto_now_add=True)
    policy_version = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user} — {self.consent_type} ({self.policy_version})"


class BulkImportJob(models.Model):
    class Status(models.TextChoices):
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"

    admin_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="bulk_import_jobs")
    file_url = models.URLField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PROCESSING)
    total_rows = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    error_log_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Import #{self.id} by {self.admin_user} ({self.status})"
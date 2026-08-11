# # from django.shortcuts import render, get_object_or_404
# # from .models import Product, Category

# # def home(request):
# #     products = Product.objects.all()[:8]  # Fetch first 8 products for home page
# #     return render(request, 'home.html', {'products': products})

# # def category_list(request):
# #     categories = Category.objects.filter(parent_category__isnull=True)
# #     return render(request, 'category.html', {'categories': categories})

# # def product_list(request):
# #     products = Product.objects.all()
# #     return render(request, 'product_list.html', {'products': products})

# # def product_detail(request, pk):
# #     product = get_object_or_404(Product, pk=pk)
# #     return render(request, 'product_detail.html', {'product': product})

# # def cart(request):
# #     return render(request, 'cart.html')

# # def refund_request(request):
# #     return render(request, 'refund.html')

# # def privacy_policy(request):
# #     return render(request, 'privacy_policy.html')

# # def terms_and_conditions(request):
# #     return render(request, 'terms_and_conditions.html')

# # def refunds_policy(request):
# #     return render(request, 'refunds.html')

# # def returns_policy(request):
# #     return render(request, 'returns.html')

# # def about_us(request):
# #     return render(request, 'about_us.html')

# # def shipping_policy(request):
# #     return render(request, 'shipping_policy.html')

# # def contact(request):
# #     return render(request, 'contact.html')

# # def profile(request):
# #     return render(request, 'profile.html')

# # def dashboard(request):
# #     return render(request, 'dashboard.html')

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.core.exceptions import PermissionDenied
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.views import LoginView
# from django.contrib.auth import login
# from django.contrib import messages
# from .forms import RegisterForm



# from .models import (
#     User, Address, Category, Product, Inventory, Coupon,
#     Order, OrderItem, BulkImportJob, StoreSettings, AuditLog
# )


# class CustomLoginView(LoginView):
#     """Role-aware login view that redirects internal staff to /dashboard/ and customers to /profile/."""
#     template_name = 'registration/login.html'

#     def get_success_url(self):
#         user = self.request.user
#         user_role = getattr(user, 'role', 'customer')
        
#         # Internal roles sent to dashboard
#         internal_roles = ['admin', 'owner', 'manager', 'employee']

#         if user.is_staff or user.is_superuser or user_role in internal_roles:
#             return '/dashboard/'
        
#         # Customers sent to profile
#         return '/profile/'
    

# # ==========================================
# # PUBLIC / CUSTOMER VIEWS
# # ==========================================

# def home(request):
#     """Storefront homepage."""
#     categories = Category.objects.filter(parent_category__isnull=True)[:8]
#     products = Product.objects.all()[:8]
#     return render(request, 'home.html', {
#         'categories': categories,
#         'products': products
#     })


# def category_list(request):
#     """View all product categories."""
#     categories = Category.objects.filter(parent_category__isnull=True)
#     return render(request, 'category.html', {'categories': categories})


# def product_list(request):
#     """View all available products."""
#     products = Product.objects.all()
#     return render(request, 'product_list.html', {'products': products})


# def product_detail(request, pk):
#     """View single product details."""
#     product = get_object_or_404(Product, pk=pk)
#     return render(request, 'product_detail.html', {'product': product})


# def cart(request):
#     """Shopping cart view."""
#     return render(request, 'cart.html')


# def refund_request(request):
#     """Form for submitting order refund requests."""
#     if request.method == 'POST':
#         messages.success(request, "Your refund request has been submitted successfully.")
#         return redirect('refund')
#     return render(request, 'refund.html')


# def contact(request):
#     """Contact & support page."""
#     if request.method == 'POST':
#         messages.success(request, "Thank you for reaching out! Our team will get back to you shortly.")
#         return redirect('contact')
#     return render(request, 'contact.html')


# @login_required
# def profile(request):
#     """Customer account dashboard, addresses, and personal details."""
#     addresses = Address.objects.filter(user=request.user)

#     if request.method == 'POST':
#         # Update user contact details
#         if 'phone' in request.POST:
#             request.user.phone = request.POST.get('phone')
#             request.user.email = request.POST.get('email')
#             request.user.save()
#             messages.success(request, "Profile details updated.")
#         # Add new address
#         elif 'line1' in request.POST:
#             Address.objects.create(
#                 user=request.user,
#                 line1=request.POST.get('line1'),
#                 landmark=request.POST.get('landmark'),
#                 pincode=request.POST.get('pincode')
#             )
#             messages.success(request, "Address added successfully.")
#         return redirect('profile')

#     return render(request, 'profile.html', {'addresses': addresses})


# def privacy_policy(request):
#     return render(request, 'privacy_policy.html')


# def terms_and_conditions(request):
#     return render(request, 'terms_and_conditions.html')


# def refunds_policy(request):
#     return render(request, 'refunds.html')


# def returns_policy(request):
#     return render(request, 'returns.html')


# def shipping_policy(request):
#     return render(request, 'shipping_policy.html')


# def about_us(request):
#     return render(request, 'about_us.html')


# # ==========================================
# # INTERNAL MANAGEMENT VIEWS
# # ==========================================

# @login_required
# def dashboard(request):
#     """Main management portal overview."""
#     user = request.user
#     user_role = getattr(user, 'role', 'customer')
    
#     # 🔒 Block regular customers if they manually type /dashboard/
#     if user_role == 'customer' and not (user.is_staff or user.is_superuser):
#         return redirect('profile')

#     orders = Order.objects.filter(order_status='pending_acceptance').order_by('-created_at')[:10]
#     pending_orders_count = Order.objects.filter(order_status='pending_acceptance').count()
#     picking_count = Order.objects.filter(picking_status='picking').count()
#     low_stock_count = Inventory.objects.filter(available_quantity__lt=5).count()

#     context = {
#         'orders': orders,
#         'pending_orders_count': pending_orders_count,
#         'picking_count': picking_count,
#         'low_stock_count': low_stock_count,
#     }
#     return render(request, 'dashboard.html', context)

# @login_required
# def manage_inventory(request):
#     """View and update product stock levels."""
#     if request.user.role not in ['manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         quantity = request.POST.get('quantity')
#         inventory = get_object_or_404(Inventory, product_id=product_id)
#         inventory.available_quantity = quantity
#         inventory.save()
#         messages.success(request, f"Updated stock for {inventory.product.name}.")
#         return redirect('manage_inventory')

#     inventory_items = Inventory.objects.select_related('product', 'product__category').all()
#     return render(request, 'manage_inventory.html', {'inventory_items': inventory_items})


# @login_required
# def manage_prices(request):
#     """Manage product prices and discounts."""
#     if request.user.role not in ['manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         price = request.POST.get('price')
#         discounted_price = request.POST.get('discounted_price') or None

#         product = get_object_or_404(Product, pk=product_id)
#         product.price = price
#         product.discounted_price = discounted_price
#         product.save()
#         messages.success(request, f"Updated pricing for {product.name}.")
#         return redirect('manage_prices')

#     products = Product.objects.all()
#     return render(request, 'manage_prices.html', {'products': products})


# @login_required
# def manage_coupons(request):
#     """Create and view promotional coupons."""
#     if request.user.role not in ['manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         Coupon.objects.create(
#             code=request.POST.get('code').upper(),
#             discount_type=request.POST.get('discount_type'),
#             discount_value=request.POST.get('discount_value'),
#             min_order_value=request.POST.get('min_order_value') or None,
#             valid_from=request.POST.get('valid_from'),
#             valid_to=request.POST.get('valid_to')
#         )
#         messages.success(request, "New promo coupon created.")
#         return redirect('manage_coupons')

#     coupons = Coupon.objects.all().order_by('-valid_to')
#     return render(request, 'manage_coupons.html', {'coupons': coupons})


# @login_required
# def bulk_import(request):
#     """Trigger bulk spreadsheet imports."""
#     if request.user.role not in ['manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         file_url = request.POST.get('file_url')
#         BulkImportJob.objects.create(
#             admin_user=request.user,
#             file_url=file_url,
#             status='processing'
#         )
#         messages.info(request, "Bulk import job created and processing started.")
#         return redirect('bulk_import')

#     import_jobs = BulkImportJob.objects.all().order_by('-created_at')[:10]
#     return render(request, 'bulk_import.html', {'import_jobs': import_jobs})


# @login_required
# def manage_staff(request):
#     """View and reassign staff user roles."""
#     if request.user.role != 'admin' and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         user_id = request.POST.get('user_id')
#         new_role = request.POST.get('role')
#         staff_user = get_object_or_404(User, pk=user_id)
#         staff_user.role = new_role
#         staff_user.save()
#         messages.success(request, f"Role for {staff_user.username} updated to {new_role}.")
#         return redirect('manage_staff')

#     staff_users = User.objects.all().order_by('username')
#     return render(request, 'manage_staff.html', {'staff_users': staff_users})


# @login_required
# def live_orders(request):
#     """Monitor active orders and update order status."""
#     if request.user.role not in ['employee', 'manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         order_id = request.POST.get('order_id')
#         new_status = request.POST.get('order_status')
#         order = get_object_or_404(Order, pk=order_id)
#         order.order_status = new_status
#         order.save()
#         messages.success(request, f"Order #{order.id} status changed to {new_status}.")
#         return redirect('live_orders')

#     orders = Order.objects.select_related('user', 'address').all().order_by('-created_at')[:20]
#     return render(request, 'live_orders.html', {'orders': orders})


# @login_required
# def item_picking(request):
#     """Order item fulfillment and stock status updates."""
#     if request.user.role not in ['employee', 'manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         item_id = request.POST.get('item_id')
#         action = request.POST.get('action')  # 'picked' or 'out_of_stock'
#         item = get_object_or_404(OrderItem, pk=item_id)

#         if action == 'picked':
#             item.fulfillment_status = 'picked'
#         elif action == 'out_of_stock':
#             item.fulfillment_status = 'out_of_stock'

#         item.save()
#         messages.success(request, f"Updated fulfillment for {item.product.name}.")
#         return redirect('item_picking')

#     order_items = OrderItem.objects.select_related('order', 'product').filter(fulfillment_status='pending')[:30]
#     return render(request, 'item_picking.html', {'order_items': order_items})


# @login_required
# def store_settings(request):
#     """Configure store operating hours and cutoff thresholds."""
#     if request.user.role != 'admin' and not request.user.is_superuser:
#         raise PermissionDenied

#     settings_obj = StoreSettings.objects.first()

#     if request.method == 'POST':
#         if not settings_obj:
#             settings_obj = StoreSettings()

#         settings_obj.open_time = request.POST.get('open_time')
#         settings_obj.close_time = request.POST.get('close_time')
#         settings_obj.instant_cutoff_time = request.POST.get('instant_cutoff_time')
#         settings_obj.save()
#         messages.success(request, "Store hours and cutoff settings saved.")
#         return redirect('store_settings')

#     return render(request, 'store_settings.html', {'settings': settings_obj})


# @login_required
# def audit_logs(request):
#     """Security audit log trail (Admin access only)."""
#     if request.user.role != 'admin' and not request.user.is_superuser:
#         raise PermissionDenied

#     logs = AuditLog.objects.select_related('user').all().order_by('-created_at')[:50]
#     return render(request, 'audit_logs.html', {'audit_logs': logs})

# def register(request):
#     """User registration view."""
#     if request.user.is_authenticated:
#         return redirect('profile')

#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)  # Auto log in user after successful registration
#             messages.success(request, f"Welcome to CnC Supermarket, {user.username}!")
#             return redirect('profile')
#     else:
#         form = RegisterForm()

#     return render(request, 'registration/register.html', {'form': form})




# @login_required
# def add_category(request):
#     """View to add a new category."""
#     if request.user.role not in ['manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         name = request.POST.get('name')
#         parent_id = request.POST.get('parent_category')
#         parent_cat = Category.objects.filter(pk=parent_id).first() if parent_id else None

#         Category.objects.create(
#             name=name,
#             parent_category=parent_cat,
#             image=request.FILES.get('image'),
#             image_url=request.POST.get('image_url') or None
#         )
#         messages.success(request, f"Category '{name}' created successfully!")
#         return redirect('category_list')

#     categories = Category.objects.all()
#     return render(request, 'add_category.html', {'categories': categories})


# @login_required
# def add_product(request):
#     """View to add a new product and initialize inventory stock."""
#     if request.user.role not in ['manager', 'admin'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         category_id = request.POST.get('category')
#         category = get_object_or_404(Category, pk=category_id)
        
#         product = Product.objects.create(
#             category=category,
#             name=request.POST.get('name'),
#             brand=request.POST.get('brand') or None,
#             unit=request.POST.get('unit'),
#             price=request.POST.get('price'),
#             discounted_price=request.POST.get('discounted_price') or None,
#             image=request.FILES.get('image'),
#             image_url=request.POST.get('image_url') or None,
#             description=request.POST.get('description') or None
#         )
        
#         initial_stock = int(request.POST.get('initial_stock', 0))
#         Inventory.objects.create(product=product, available_quantity=initial_stock)

#         messages.success(request, f"Product '{product.name}' added successfully!")
#         return redirect('product_list')

#     categories = Category.objects.all()
#     return render(request, 'add_product.html', {'categories': categories})































from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .forms import RegisterForm
from .models import (
    User, Address, Category, Product, Inventory, Coupon,
    Order, OrderItem, BulkImportJob, StoreSettings, AuditLog
)

# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

class CustomLoginView(LoginView):
    """
    Role-aware login view that redirects internal roles (admin, owner, manager, employee)
    to /dashboard/ and regular customers to /profile/.
    """
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        user_role = getattr(user, 'role', 'customer')
        
        internal_roles = ['admin', 'owner', 'manager', 'employee']

        if user.is_staff or user.is_superuser or user_role in internal_roles:
            return '/dashboard/'
        
        return '/profile/'


def register(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto log in user after successful registration
            messages.success(request, f"Welcome to CnC Supermarket, {user.username}!")
            return redirect('profile')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


# ==========================================
# PUBLIC / CUSTOMER VIEWS
# ==========================================

def home(request):
    """Storefront homepage."""
    categories = Category.objects.filter(parent_category__isnull=True)[:8]
    products = Product.objects.all()[:8]
    return render(request, 'home.html', {
        'categories': categories,
        'products': products
    })


def category_list(request):
    """View all product categories."""
    categories = Category.objects.filter(parent_category__isnull=True)
    return render(request, 'category.html', {'categories': categories})


def product_list(request):
    """View all available products."""
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def product_detail(request, pk):
    """View single product details."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


def cart(request):
    """Shopping cart view."""
    return render(request, 'cart.html')


def refund_request(request):
    """Form for submitting order refund requests."""
    if request.method == 'POST':
        messages.success(request, "Your refund request has been submitted successfully.")
        return redirect('refund')
    return render(request, 'refund.html')


def contact(request):
    """Contact & support page."""
    if request.method == 'POST':
        messages.success(request, "Thank you for reaching out! Our team will get back to you shortly.")
        return redirect('contact')
    return render(request, 'contact.html')


@login_required
def profile(request):
    """Customer account dashboard, addresses, and personal details."""
    addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        if 'phone' in request.POST:
            request.user.phone = request.POST.get('phone')
            request.user.email = request.POST.get('email')
            request.user.save()
            messages.success(request, "Profile details updated.")
        elif 'line1' in request.POST:
            Address.objects.create(
                user=request.user,
                line1=request.POST.get('line1'),
                landmark=request.POST.get('landmark'),
                pincode=request.POST.get('pincode')
            )
            messages.success(request, "Address added successfully.")
        return redirect('profile')

    return render(request, 'profile.html', {'addresses': addresses})


def privacy_policy(request):
    return render(request, 'privacy_policy.html')


def terms_and_conditions(request):
    return render(request, 'terms_and_conditions.html')


def refunds_policy(request):
    return render(request, 'refunds.html')


def returns_policy(request):
    return render(request, 'returns.html')


def shipping_policy(request):
    return render(request, 'shipping_policy.html')


def about_us(request):
    return render(request, 'about_us.html')


# ==========================================
# INTERNAL MANAGEMENT VIEWS
# ==========================================

@login_required
def dashboard(request):
    """Main management portal overview."""
    user = request.user
    user_role = getattr(user, 'role', 'customer')
    
    # Block regular customers if they manually navigate to /dashboard/
    if user_role == 'customer' and not (user.is_staff or user.is_superuser):
        return redirect('profile')

    orders = Order.objects.filter(order_status='pending_acceptance').order_by('-created_at')[:10]
    pending_orders_count = Order.objects.filter(order_status='pending_acceptance').count()
    picking_count = Order.objects.filter(picking_status='picking').count()
    low_stock_count = Inventory.objects.filter(available_quantity__lt=5).count()

    context = {
        'orders': orders,
        'pending_orders_count': pending_orders_count,
        'picking_count': picking_count,
        'low_stock_count': low_stock_count,
    }
    return render(request, 'dashboard.html', context)


@login_required
def add_category(request):
    """View to add new category with file/url image upload."""
    if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_category')
        parent_cat = Category.objects.filter(pk=parent_id).first() if parent_id else None

        Category.objects.create(
            name=name,
            parent_category=parent_cat,
            image=request.FILES.get('image'),
            image_url=request.POST.get('image_url') or None
        )
        messages.success(request, f"Category '{name}' created successfully!")
        return redirect('category_list')

    categories = Category.objects.all()
    return render(request, 'add_category.html', {'categories': categories})


@login_required
def add_product(request):
    """View to add new product with file/url image upload and initial stock."""
    if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        category_id = request.POST.get('category')
        category = get_object_or_404(Category, pk=category_id)
        
        product = Product.objects.create(
            category=category,
            name=request.POST.get('name'),
            brand=request.POST.get('brand') or None,
            unit=request.POST.get('unit'),
            price=request.POST.get('price'),
            discounted_price=request.POST.get('discounted_price') or None,
            image=request.FILES.get('image'),
            image_url=request.POST.get('image_url') or None,
            description=request.POST.get('description') or None
        )
        
        initial_stock = int(request.POST.get('initial_stock', 0))
        Inventory.objects.create(product=product, available_quantity=initial_stock)

        messages.success(request, f"Product '{product.name}' added successfully!")
        return redirect('product_list')

    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})


@login_required
def manage_inventory(request):
    """View and update product stock levels."""
    if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        inventory = get_object_or_404(Inventory, product_id=product_id)
        inventory.available_quantity = quantity
        inventory.save()
        messages.success(request, f"Updated stock for {inventory.product.name}.")
        return redirect('manage_inventory')

    inventory_items = Inventory.objects.select_related('product', 'product__category').all()
    return render(request, 'manage_inventory.html', {'inventory_items': inventory_items})


@login_required
def manage_prices(request):
    """Manage product prices and discounts."""
    if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        price = request.POST.get('price')
        discounted_price = request.POST.get('discounted_price') or None

        product = get_object_or_404(Product, pk=product_id)
        product.price = price
        product.discounted_price = discounted_price
        product.save()
        messages.success(request, f"Updated pricing for {product.name}.")
        return redirect('manage_prices')

    products = Product.objects.all()
    return render(request, 'manage_prices.html', {'products': products})


@login_required
def manage_coupons(request):
    """Create and view promotional coupons."""
    if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        Coupon.objects.create(
            code=request.POST.get('code').upper(),
            discount_type=request.POST.get('discount_type'),
            discount_value=request.POST.get('discount_value'),
            min_order_value=request.POST.get('min_order_value') or None,
            valid_from=request.POST.get('valid_from'),
            valid_to=request.POST.get('valid_to')
        )
        messages.success(request, "New promo coupon created.")
        return redirect('manage_coupons')

    coupons = Coupon.objects.all().order_by('-valid_to')
    return render(request, 'manage_coupons.html', {'coupons': coupons})


@login_required
def bulk_import(request):
    """Trigger bulk spreadsheet imports."""
    if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        file_url = request.POST.get('file_url')
        BulkImportJob.objects.create(
            admin_user=request.user,
            file_url=file_url,
            status='processing'
        )
        messages.info(request, "Bulk import job created and processing started.")
        return redirect('bulk_import')

    import_jobs = BulkImportJob.objects.all().order_by('-created_at')[:10]
    return render(request, 'bulk_import.html', {'import_jobs': import_jobs})


@login_required
def manage_staff(request):
    """View and reassign staff user roles."""
    if request.user.role not in ['admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        staff_user = get_object_or_404(User, pk=user_id)
        staff_user.role = new_role
        staff_user.save()
        messages.success(request, f"Role for {staff_user.username} updated to {new_role}.")
        return redirect('manage_staff')

    staff_users = User.objects.all().order_by('username')
    return render(request, 'manage_staff.html', {'staff_users': staff_users})


@login_required
def live_orders(request):
    """Monitor active orders and update order status."""
    if request.user.role not in ['employee', 'manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('order_status')
        order = get_object_or_404(Order, pk=order_id)
        order.order_status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} status changed to {new_status}.")
        return redirect('live_orders')

    orders = Order.objects.select_related('user', 'address').all().order_by('-created_at')[:20]
    return render(request, 'live_orders.html', {'orders': orders})


@login_required
def item_picking(request):
    """Order item fulfillment and stock status updates."""
    if request.user.role not in ['employee', 'manager', 'admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        action = request.POST.get('action')
        item = get_object_or_404(OrderItem, pk=item_id)

        if action == 'picked':
            item.fulfillment_status = 'picked'
        elif action == 'out_of_stock':
            item.fulfillment_status = 'out_of_stock'

        item.save()
        messages.success(request, f"Updated fulfillment for {item.product.name}.")
        return redirect('item_picking')

    order_items = OrderItem.objects.select_related('order', 'product').filter(fulfillment_status='pending')[:30]
    return render(request, 'item_picking.html', {'order_items': order_items})


@login_required
def store_settings(request):
    """Configure store operating hours and cutoff thresholds."""
    if request.user.role not in ['admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    settings_obj = StoreSettings.objects.first()

    if request.method == 'POST':
        if not settings_obj:
            settings_obj = StoreSettings()

        settings_obj.open_time = request.POST.get('open_time')
        settings_obj.close_time = request.POST.get('close_time')
        settings_obj.instant_cutoff_time = request.POST.get('instant_cutoff_time')
        settings_obj.save()
        messages.success(request, "Store hours and cutoff settings saved.")
        return redirect('store_settings')

    return render(request, 'store_settings.html', {'settings': settings_obj})


@login_required
def audit_logs(request):
    """Security audit log trail."""
    if request.user.role not in ['admin', 'owner'] and not request.user.is_superuser:
        raise PermissionDenied

    logs = AuditLog.objects.select_related('user').all().order_by('-created_at')[:50]
    return render(request, 'audit_logs.html', {'audit_logs': logs})
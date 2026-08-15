import csv
import io
import json
# import pandas as pd
import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Category
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .models import Product, Order, Category, Inventory

from .forms import RegisterForm
from .models import (
    User, Address, Category, Product, Inventory, Coupon,
    Order, OrderItem, BulkImportJob, StoreSettings, AuditLog, RefundRequest
)


# ==========================================
# AUTHENTICATION VIEWS
# ==========================================

class CustomLoginView(LoginView):
    """Role-aware login view redirecting staff/admin to dashboard and customers to profile."""
    template_name = 'registration/login.html'

    def get_success_url(self):
        user = self.request.user
        user_role = getattr(user, 'role', 'customer')
        internal_roles = ['admin', 'owner', 'manager', 'employee']

        if user.is_staff or user.is_superuser or user_role in internal_roles:
            return '/dashboard/'
        return '/profile/'

# In store/views.py
import re
import re
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q

User = get_user_model()

def register(request):
    """Customer registration with strict 10-digit phone validation and duplicate handling."""
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next', request.POST.get('next', 'home'))

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        # 1. Strict 10-Digit Mobile Number Validation (Indian standard: starts with 6-9)
        if not re.match(r'^[6-9]\d{9}$', phone):
            messages.error(request, "Please enter a valid 10-digit mobile number starting with 6, 7, 8, or 9.")
            return render(request, 'register.html', {
                'full_name': full_name,
                'phone': phone,
                'email': email,
                'next': next_url
            })

        # 2. Password Confirmation Check
        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return render(request, 'register.html', {
                'full_name': full_name,
                'phone': phone,
                'email': email,
                'next': next_url
            })

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'register.html', {
                'full_name': full_name,
                'phone': phone,
                'email': email,
                'next': next_url
            })

        # 3. Check for existing username or phone number in DB
        username_exists = User.objects.filter(username=phone).exists()
        phone_exists = hasattr(User, 'phone') and User.objects.filter(phone=phone).exists()

        if username_exists or phone_exists:
            messages.info(request, "An account with this mobile number is already registered. Please sign in.")
            return redirect(f"/login/?next={next_url}")

        # 4. Create User Record
        try:
            user = User.objects.create_user(
                username=phone,
                email=email or '',
                password=password
            )
            if hasattr(user, 'phone'):
                user.phone = phone
            if hasattr(user, 'role'):
                user.role = 'customer'

            # Save full name
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            if len(name_parts) > 1:
                user.last_name = name_parts[1]

            user.save()

            # Automatically log in the new user
            login(request, user)
            messages.success(request, f"Welcome to CnC Supermarket, {user.first_name or user.username}!")
            return redirect(next_url if next_url != 'home' else 'home')

        except Exception as e:
            messages.error(request, f"Registration error: {str(e)}")
            return render(request, 'register.html', {
                'full_name': full_name,
                'phone': phone,
                'email': email,
                'next': next_url
            })

    return render(request, 'register.html', {'next': next_url})

import re
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Q

User = get_user_model()

def login_view(request):
    """Sign-in supporting 10-digit Mobile Phone, Username, or Email."""
    if request.user.is_authenticated:
        return redirect('home')

    next_url = request.GET.get('next', request.POST.get('next', 'home'))

    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not identifier or not password:
            messages.error(request, "Please enter your mobile number/email and password.")
            return render(request, 'login.html', {'next': next_url, 'identifier': identifier})

        # Match by phone, username, or email
        user_query = Q(username__iexact=identifier)
        if hasattr(User, 'phone'):
            user_query |= Q(phone=identifier)
        if '@' in identifier:
            user_query |= Q(email__iexact=identifier)

        user_obj = User.objects.filter(user_query).first()
        username_to_auth = user_obj.username if user_obj else identifier

        # Authenticate
        user = authenticate(request, username=username_to_auth, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url if next_url and next_url != 'home' else 'home')
            else:
                messages.error(request, "Your account is deactivated. Please contact support.")
        else:
            messages.error(request, "Invalid mobile number, username, or password.")

    return render(request, 'login.html', {'next': next_url})

# Define alias for any URL pattern using user_login
user_login = login_view


def logout_view(request):
    """User sign-out view."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

# Define alias for any URL pattern using user_logout
user_logout = logout_view



def user_logout(request):
    """Log out customer and redirect to home."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')

# ==========================================
# PUBLIC / STOREFRONT VIEWS
# ==========================================
# In store/views.py

def home(request):
    """Storefront homepage with clean integer cart mapping."""
    categories = Category.objects.filter(parent_category__isnull=True)[:8]
    products = Product.objects.all()[:8]
    
    cart = request.session.get('cart', {})
    cart_quantities = {}

    for pid, item in cart.items():
        if isinstance(item, dict):
            cart_quantities[str(pid)] = int(item.get('quantity', 0))
        elif isinstance(item, int):
            cart_quantities[str(pid)] = item

    return render(request, 'home.html', {
        'categories': categories,
        'products': products,
        'cart_quantities_json': json.dumps(cart_quantities)
    })



def product_list(request):
    """View all available products."""
    products = Product.objects.all()
    return render(request, 'product_list.html', {'products': products})


def product_detail(request, pk):
    """View single product details."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


# In store/views.py

@login_required
def refund_request(request):
    """Customer view: Submit a refund/return request with mandatory media proof."""
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        reason = request.POST.get('reason')
        description = request.POST.get('description', '').strip()
        proof_file = request.FILES.get('proof_file')

        if not order_id or not description:
            messages.error(request, "Please select an order and provide a detailed reason.")
            return redirect('refund')

        if not proof_file:
            messages.error(request, "Please upload an image or video proof for verification.")
            return redirect('refund')

        order = get_object_or_404(Order, pk=order_id, user=request.user)

        # Create refund request ticket with attached proof
        RefundRequest.objects.create(
            user=request.user,
            order=order,
            reason=reason,
            description=description,
            proof_file=proof_file,
            amount_requested=order.total_amount,
            status='pending'
        )

        messages.success(request, f"Refund request for Order #{order.id} submitted! Our team will inspect the proof and update you shortly.")
        return redirect('profile')

    my_refunds = RefundRequest.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'refund.html', {
        'orders': user_orders,
        'my_refunds': my_refunds
    })

@login_required
def manage_refunds(request):
    """Staff/Admin view: Review, inspect media proof, and update refund tickets."""
    user = request.user
    user_role = getattr(user, 'role', 'customer')
    if user_role == 'customer' and not (user.is_staff or user.is_superuser):
        raise PermissionDenied

    if request.method == 'POST':
        refund_id = request.POST.get('refund_id')
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '').strip()

        refund_obj = get_object_or_404(RefundRequest, pk=refund_id)
        refund_obj.status = new_status
        if admin_notes:
            refund_obj.admin_notes = admin_notes
        refund_obj.save()

        messages.success(request, f"Refund #{refund_obj.id} status updated to {new_status.title()}.")
        return redirect('manage_refunds')

    refund_tickets = RefundRequest.objects.select_related('user', 'order').all().order_by('-created_at')
    return render(request, 'manage_refunds.html', {'refund_tickets': refund_tickets})


def contact(request):
    """Contact & support page."""
    if request.method == 'POST':
        messages.success(request, "Thank you for reaching out! Our team will get back to you shortly.")
        return redirect('contact')
    return render(request, 'contact.html')

# In store/views.py

@login_required
def profile(request):
    """Customer account dashboard, saved addresses, and past order history."""
    addresses = Address.objects.filter(user=request.user)
    # Fetch all past orders for the logged-in customer, latest first
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')

    if request.method == 'POST':
        # Update contact information
        if 'phone' in request.POST:
            request.user.phone = request.POST.get('phone', '').strip()
            request.user.email = request.POST.get('email', '').strip()
            request.user.save()
            messages.success(request, "Profile contact details updated successfully.")
        
        # Add a new saved address
        elif 'line1' in request.POST:
            line1 = request.POST.get('line1', '').strip()
            landmark = request.POST.get('landmark', '').strip()
            pincode = request.POST.get('pincode', '').strip()

            if line1 and pincode:
                Address.objects.create(
                    user=request.user,
                    line1=line1,
                    landmark=landmark or None,
                    pincode=pincode
                )
                messages.success(request, "New address saved successfully.")
            else:
                messages.error(request, "Please enter all required address fields.")
                
        return redirect('profile')

    context = {
        'addresses': addresses,
        'orders': orders,
    }
    return render(request, 'profile.html', context)


@login_required
def order_detail(request, order_id):
    """View full receipt details of a specific past order."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_items = OrderItem.objects.select_related('product').filter(order=order)

    return render(request, 'order_detail.html', {
        'order': order,
        'order_items': order_items
    })

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
# CART HELPER FUNCTIONS & API VIEWS
# ==========================================

def _get_cart(request):
    """Retrieve session cart."""
    return request.session.get('cart', {})


@require_POST
def add_to_cart(request):
    """Add product to session cart via Form POST."""
    product_id = request.POST.get('product_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if not product_id:
        return JsonResponse({'status': 'error', 'message': 'Missing product ID'}, status=400)

    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += quantity
    else:
        cart[product_id_str] = {'quantity': quantity}

    request.session['cart'] = cart
    request.session.modified = True

    total_count = sum(item['quantity'] for item in cart.values())

    return JsonResponse({
        'status': 'success',
        'cart_count': total_count
    })

def update_cart_quantity(request):
    """Interactive endpoint to update or remove item in session cart."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        product_id = str(data.get('product_id'))
        action = data.get('action')

        cart = request.session.get('cart', {})
        if not isinstance(cart, dict):
            cart = {}

        if product_id in cart:
            if not isinstance(cart[product_id], dict):
                cart[product_id] = {'quantity': int(cart[product_id]) if str(cart[product_id]).isdigit() else 0}
        else:
            cart[product_id] = {'quantity': 0}

        current_qty = int(cart[product_id].get('quantity', 0))

        if action == 'increase':
            cart[product_id]['quantity'] = current_qty + 1
        elif action == 'decrease':
            cart[product_id]['quantity'] = current_qty - 1
            if cart[product_id]['quantity'] <= 0:
                del cart[product_id]
        elif action == 'remove':
            if product_id in cart:
                del cart[product_id]

        request.session['cart'] = cart
        request.session.modified = True

        total_items = sum(
            int(item.get('quantity', 0)) if isinstance(item, dict) else int(item)
            for item in cart.values()
        )
        product_qty = cart.get(product_id, {}).get('quantity', 0) if product_id in cart else 0

        return JsonResponse({
            'status': 'success',
            'cart_count': total_items,
            'product_qty': product_qty
        })

    return JsonResponse({'status': 'error'}, status=400)


# In store/views.py

def cart(request):
    """Shopping cart view calculating subtotal, delivery fee, and grand total."""
    session_cart = request.session.get('cart', {})
    cart_items = []
    subtotal = 0

    if isinstance(session_cart, dict) and session_cart:
        # Extract integer product IDs from session keys
        product_ids = [int(pid) for pid in session_cart.keys() if str(pid).isdigit()]
        products = Product.objects.filter(id__in=product_ids)
        product_map = {p.id: p for p in products}

        for pid_str, item in session_cart.items():
            if not str(pid_str).isdigit():
                continue
            pid = int(pid_str)
            if pid in product_map:
                product = product_map[pid]
                
                # Support both dict {'quantity': X} and direct int formats
                if isinstance(item, dict):
                    qty = int(item.get('quantity', 0))
                else:
                    qty = int(item) if str(item).isdigit() else 0

                if qty <= 0:
                    continue

                # Use discounted price if available, else regular price
                unit_price = product.discounted_price if product.discounted_price else product.price
                item_total = unit_price * qty
                subtotal += item_total

                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'unit_price': unit_price,
                    'total_price': item_total,
                })

    # Free delivery above ₹100, otherwise ₹29
    delivery_fee = 29 if (0 < subtotal < 100) else 0
    grand_total = subtotal + delivery_fee

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)


def clear_cart(request):
    """Helper view to flush the cart session."""
    request.session['cart'] = {}
    request.session.modified = True
    return redirect('cart')

# ==========================================
# CHECKOUT & ORDER PLACEMENT
# ==========================================
# In store/views.py

# In store/views.py

# In store/views.py

@login_required
def checkout(request):
    """
    Checkout view:
    - Enforces mandatory phone number and updates user profile.
    - Handles picking a saved address OR adding a new one via `selected_address`.
    """
    session_cart = request.session.get('cart', {})
    if not session_cart:
        messages.warning(request, "Your cart is empty. Please add items before checking out.")
        return redirect('product_list')

    # Fetch product records from database
    valid_pids = [int(pid) for pid in session_cart.keys() if str(pid).isdigit()]
    products = Product.objects.filter(id__in=valid_pids)
    product_map = {p.id: p for p in products}

    cart_items = []
    subtotal = 0

    for pid_str, item in session_cart.items():
        if not str(pid_str).isdigit():
            continue
        pid = int(pid_str)
        if pid in product_map:
            product = product_map[pid]
            qty = int(item.get('quantity', 0)) if isinstance(item, dict) else int(item)
            if qty <= 0:
                continue

            unit_price = product.discounted_price if product.discounted_price else product.price
            item_total = unit_price * qty
            subtotal += item_total

            cart_items.append({
                'product': product,
                'quantity': qty,
                'unit_price': unit_price,
                'total_price': item_total
            })

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('product_list')

    delivery_fee = 29 if (0 < subtotal < 100) else 0
    grand_total = subtotal + delivery_fee
    user_addresses = Address.objects.filter(user=request.user)

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        selected_address = request.POST.get('selected_address')
        payment_method = request.POST.get('payment_method', 'COD')
        delivery_mode = request.POST.get('delivery_mode', 'instant')

        # 1. MANDATORY PHONE NUMBER VALIDATION
        if not phone:
            messages.error(request, "Phone number is compulsory to proceed with checkout.")
            return redirect('checkout')

        # Update User Profile with Phone & Email
        user_updated = False
        if request.user.phone != phone:
            request.user.phone = phone
            user_updated = True
        if email and request.user.email != email:
            request.user.email = email
            user_updated = True
        if user_updated:
            request.user.save()

        # 2. ADDRESS RESOLUTION
        address = None
        if selected_address and selected_address != 'new' and selected_address.isdigit():
            address = get_object_or_404(Address, pk=int(selected_address), user=request.user)
        else:
            line1 = request.POST.get('line1', '').strip()
            landmark = request.POST.get('landmark', '').strip()
            pincode = request.POST.get('pincode', '').strip()

            if not line1 or not pincode:
                messages.error(request, "Please enter a valid delivery address and pincode.")
                return redirect('checkout')

            address = Address.objects.create(
                user=request.user,
                line1=line1,
                landmark=landmark or None,
                pincode=pincode
            )

        # 3. CREATE ORDER RECORD
        order = Order.objects.create(
            user=request.user,
            address=address,
            delivery_mode=delivery_mode,
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=grand_total,
            order_status='pending_acceptance'
        )

        # 4. CREATE ORDER ITEMS
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                unit_price=item['unit_price'],
                total_price=item['total_price']
            )

        # 5. CLEAR SESSION CART
        request.session['cart'] = {}
        request.session.modified = True

        messages.success(request, f"Order #{order.id} placed successfully!")
        return redirect('order_success', order_id=order.id)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total,
        'addresses': user_addresses,
    }
    return render(request, 'checkout.html', context)


@login_required
def order_success(request, order_id):
    """Order confirmation and receipt page."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    order_items = OrderItem.objects.select_related('product').filter(order=order)

    return render(request, 'order_success.html', {
        'order': order,
        'order_items': order_items
    })



# ==========================================
# INTERNAL MANAGEMENT VIEWS
# ==========================================
# In store/views.py
# In store/views.py

def is_staff_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_staff_check, login_url='/accounts/login/')
def dashboard(request):
    # 1. Order Status Counts
    pending_orders_count = Order.objects.filter(order_status='pending_acceptance').count()
    active_orders_count = Order.objects.filter(
        order_status__in=['accepted', 'packing', 'out_for_delivery']
    ).count()
    
    # Check refund claim count safely if model exists, otherwise 0
    pending_refunds_count = 0
    try:
        from .models import Refund
        pending_refunds_count = Refund.objects.filter(status='pending').count()
    except Exception:
        pass

    # 2. Inventory / Low Stock calculations
    try:
        low_stock_count = Product.objects.filter(inventory__quantity__lt=10).count()
        low_stock_items = Product.objects.filter(inventory__quantity__lt=10).select_related('inventory')[:6]
    except Exception:
        low_stock_count = 0
        low_stock_items = []

    # 3. Recent Orders
    recent_orders = Order.objects.select_related('user', 'address').prefetch_related('items').order_by('-id')[:10]

    context = {
        'pending_orders_count': pending_orders_count,
        'active_orders_count': active_orders_count,
        'pending_refunds_count': pending_refunds_count,
        'low_stock_count': low_stock_count,
        'recent_orders': recent_orders,
        'low_stock_items': low_stock_items,
    }
    return render(request, 'dashboard.html', context)

def is_staff_check(user):
    """Checks if the user is authenticated and is a staff member or superuser."""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# 1. Customer-Facing Category Views (Resolves NoReverseMatch on homepage)
def category_list(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'category_list.html', {'categories': categories})


def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    # Filter products belonging to this category
    products = Product.objects.filter(category=category)
    return render(request, 'category_detail.html', {
        'category': category,
        'products': products
    })


# 2. Staff Management Category Views (Resolves AttributeError in urls.py)
@user_passes_test(is_staff_check, login_url='/accounts/login/')
def manage_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'manage_categories.html', {'categories': categories})


@user_passes_test(is_staff_check, login_url='/accounts/login/')
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        parent_id = request.POST.get('parent_category')
        image = request.FILES.get('image')
        image_url = request.POST.get('image_url')

        if name:
            parent = None
            if parent_id:
                try:
                    parent = Category.objects.get(id=parent_id)
                except Category.DoesNotExist:
                    parent = None

            category = Category(
                name=name,
                parent_category=parent if hasattr(Category, 'parent_category') else None
            )

            if image:
                category.image = image
            if image_url and hasattr(category, 'image_url'):
                category.image_url = image_url

            category.save()
            return redirect('manage_categories')

    categories = Category.objects.all().order_by('name')
    return render(request, 'add_category.html', {'categories': categories})


@user_passes_test(is_staff_check, login_url='/accounts/login/')
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        image = request.FILES.get('image')
        image_url = request.POST.get('image_url')

        if name:
            category.name = name
            if image:
                category.image = image
            if image_url and hasattr(category, 'image_url'):
                category.image_url = image_url
            category.save()
            return redirect('manage_categories')

    return render(request, 'edit_category.html', {'category': category})


@user_passes_test(is_staff_check, login_url='/accounts/login/')
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        category.delete()
    return redirect('manage_categories')

    
@login_required
def live_orders(request):
    """Dedicated live order management screen with quick status transitions."""
    user = request.user
    user_role = getattr(user, 'role', 'customer')

    if user_role == 'customer' and not (user.is_staff or user.is_superuser):
        raise PermissionDenied

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('order_status')
        
        order = get_object_or_404(Order, pk=order_id)
        order.order_status = new_status
        
        if new_status == 'accepted' and not order.accepted_by:
            order.accepted_by = request.user
            
        order.save()
        messages.success(request, f"Order #{order.id} status updated to {new_status.replace('_', ' ').title()}.")
        return redirect('live_orders')

    orders = Order.objects.select_related('user', 'address').prefetch_related('items__product').all().order_by('-created_at')
    return render(request, 'live_orders.html', {'orders': orders})

@login_required
def add_category(request):
    """View to add new category."""
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
    """View to add new product and initialize stock."""
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
    """View to upload CSV/Excel files and parse product data."""
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        file_url = request.POST.get('file_url')

        if not uploaded_file and not file_url:
            messages.error(request, "Please select a file to upload or enter a valid file URL.")
            return redirect('bulk_import')

        job = BulkImportJob.objects.create(
            admin_user=request.user,
            file_url=file_url if file_url else getattr(uploaded_file, 'name', 'local_upload'),
            status='processing'
        )

        success = 0
        errors = 0

        try:
            if uploaded_file:
                file_name = uploaded_file.name.lower()
                if file_name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif file_name.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(uploaded_file)
                else:
                    raise ValueError("Unsupported file format. Please upload a .csv or .xlsx file.")
            else:
                resp = requests.get(file_url)
                if file_url.lower().endswith('.csv'):
                    df = pd.read_csv(io.StringIO(resp.text))
                else:
                    df = pd.read_excel(io.BytesIO(resp.content))

            df.columns = df.columns.str.strip().str.lower()
            job.total_rows = len(df)

            for _, row in df.iterrows():
                try:
                    category_name = str(row.get('category_name', '')).strip()
                    product_name = str(row.get('product_name', '')).strip()

                    if not category_name or not product_name:
                        errors += 1
                        continue

                    category, _ = Category.objects.get_or_create(name=category_name)

                    price = float(row.get('price', 0))
                    discounted_price = float(row.get('discounted_price')) if pd.notna(row.get('discounted_price')) and row.get('discounted_price') != '' else None
                    stock_qty = int(row.get('available_quantity', 0)) if pd.notna(row.get('available_quantity')) else 0

                    product, _ = Product.objects.update_or_create(
                        name=product_name,
                        defaults={
                            'category': category,
                            'brand': str(row.get('brand', '')) if pd.notna(row.get('brand')) else '',
                            'unit': str(row.get('unit', '1 unit')) if pd.notna(row.get('unit')) else '1 unit',
                            'price': price,
                            'discounted_price': discounted_price,
                            'image_url': str(row.get('image_url', '')) if pd.notna(row.get('image_url')) else '',
                            'description': str(row.get('description', '')) if pd.notna(row.get('description')) else '',
                        }
                    )

                    Inventory.objects.update_or_create(
                        product=product,
                        defaults={'available_quantity': stock_qty}
                    )

                    success += 1

                except Exception:
                    errors += 1

            job.status = 'completed' if errors == 0 else 'failed' if success == 0 else 'completed'
            job.success_count = success
            job.error_count = errors
            job.save()

            messages.success(request, f"Import finished! {success} products added/updated, {errors} errors.")

        except Exception as e:
            job.status = 'failed'
            job.error_count = job.total_rows if job.total_rows > 0 else 1
            job.save()
            messages.error(request, f"Failed to process file: {str(e)}")

        return redirect('bulk_import')

    import_jobs = BulkImportJob.objects.all().order_by('-created_at')[:10]
    return render(request, 'bulk_import.html', {'import_jobs': import_jobs})


@login_required
def download_sample_import(request):
    """Generates and serves a sample CSV file for bulk product uploads."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cnc_product_import_sample.csv"'

    writer = csv.writer(response)
    writer.writerow(['category_name', 'product_name', 'brand', 'unit', 'price', 'discounted_price', 'available_quantity', 'image_url', 'description'])
    writer.writerow(['Dairy & Eggs', 'Amul Taaza T-Special Milk', 'Amul', '500 ml', '27.00', '', '50', 'https://via.placeholder.com/300', 'Pasteurised toned milk'])
    writer.writerow(['Snacks', 'Lays Classic Salted Chips', 'Lays', '50 g', '20.00', '18.00', '100', 'https://via.placeholder.com/300', 'Crispy salted potato chips'])

    return response


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

from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin_or_manager(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff or getattr(user, 'role', None) in ['admin', 'manager'])

@login_required
@user_passes_test(is_admin_or_manager)
def staff_management(request):
    """View to manage staff members and roles."""
    staff_members = User.objects.filter(is_staff=True) | User.objects.exclude(role='customer') if hasattr(User, 'role') else User.objects.filter(is_staff=True)
    return render(request, 'store/staff_management.html', {
        'staff_members': staff_members.distinct()
    })

































































































































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


# def cart(request):
#     """Shopping cart page with item details and totals."""
#     cart_data = _get_cart(request)
#     cart_items = []
#     subtotal = 0

#     for product_id, item in cart_data.items():
#         product = Product.objects.filter(pk=product_id).first()
#         if product:
#             item_total = float(product.price if not product.discounted_price else product.discounted_price) * item['quantity']
#             subtotal += item_total
#             cart_items.append({
#                 'product': product,
#                 'quantity': item['quantity'],
#                 'item_total': item_total,
#             })

#     delivery_fee = 29 if subtotal < 500 and subtotal > 0 else 0
#     grand_total = subtotal + delivery_fee

#     context = {
#         'cart_items': cart_items,
#         'subtotal': subtotal,
#         'delivery_fee': delivery_fee,
#         'grand_total': grand_total,
#     }
#     return render(request, 'cart.html', context)


# def add_to_cart(request):
#     """AJAX view to add or update item in cart."""
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         product_id = str(data.get('product_id'))
#         quantity = int(data.get('quantity', 1))

#         product = get_object_or_404(Product, pk=product_id)
#         cart = request.session.get('cart', {})

#         if product_id in cart:
#             cart[product_id]['quantity'] += quantity
#         else:
#             cart[product_id] = {
#                 'name': product.name,
#                 'price': str(product.discounted_price or product.price),
#                 'quantity': quantity
#             }

#         request.session['cart'] = cart
#         total_items = sum(item['quantity'] for item in cart.values())

#         return JsonResponse({'status': 'success', 'cart_count': total_items, 'message': f'{product.name} added to cart.'})
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)































# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import login
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.views import LoginView
# from django.contrib import messages
# from django.core.exceptions import PermissionDenied

# from .forms import RegisterForm
# from .models import (
#     User, Address, Category, Product, Inventory, Coupon,
#     Order, OrderItem, BulkImportJob, StoreSettings, AuditLog
# )

# # ==========================================
# # AUTHENTICATION VIEWS
# # ==========================================

# class CustomLoginView(LoginView):
#     """
#     Role-aware login view that redirects internal roles (admin, owner, manager, employee)
#     to /dashboard/ and regular customers to /profile/.
#     """
#     template_name = 'registration/login.html'

#     def get_success_url(self):
#         user = self.request.user
#         user_role = getattr(user, 'role', 'customer')
        
#         internal_roles = ['admin', 'owner', 'manager', 'employee']

#         if user.is_staff or user.is_superuser or user_role in internal_roles:
#             return '/dashboard/'
        
#         return '/profile/'


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
#         if 'phone' in request.POST:
#             request.user.phone = request.POST.get('phone')
#             request.user.email = request.POST.get('email')
#             request.user.save()
#             messages.success(request, "Profile details updated.")
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
    
#     # Block regular customers if they manually navigate to /dashboard/
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
# def add_category(request):
#     """View to add new category with file/url image upload."""
#     if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
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
#     """View to add new product with file/url image upload and initial stock."""
#     if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
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


# @login_required
# def manage_inventory(request):
#     """View and update product stock levels."""
#     if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
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
#     if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
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
#     if request.user.role not in ['manager', 'admin', 'owner'] and not request.user.is_superuser:
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

# import pandas as pd
# import io
# import requests
# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import BulkImportJob, Category, Product, Inventory


# @login_required
# def bulk_import(request):
#     """View to upload CSV/Excel files and parse product data."""
#     if request.method == 'POST':
#         uploaded_file = request.FILES.get('file')
#         file_url = request.POST.get('file_url')

#         if not uploaded_file and not file_url:
#             messages.error(request, "Please select a file to upload or enter a valid file URL.")
#             return redirect('bulk_import')

#         # 1. Create the tracking job
#         job = BulkImportJob.objects.create(
#             admin_user=request.user,
#             file_url=file_url if file_url else getattr(uploaded_file, 'name', 'local_upload'),
#             status='processing'
#         )

#         success = 0
#         errors = 0

#         try:
#             # 2. Read file into a Pandas DataFrame
#             if uploaded_file:
#                 file_name = uploaded_file.name.lower()
#                 if file_name.endswith('.csv'):
#                     df = pd.read_csv(uploaded_file)
#                 elif file_name.endswith(('.xlsx', '.xls')):
#                     df = pd.read_excel(uploaded_file)
#                 else:
#                     raise ValueError("Unsupported file format. Please upload a .csv or .xlsx file.")
#             else:
#                 # Fetch remote URL content
#                 resp = requests.get(file_url)
#                 if file_url.lower().endswith('.csv'):
#                     df = pd.read_csv(io.StringIO(resp.text))
#                 else:
#                     df = pd.read_excel(io.BytesIO(resp.content))

#             # Clean dataframe headers (strip whitespace and convert to lower)
#             df.columns = df.columns.str.strip().str.lower()
#             job.total_rows = len(df)

#             # 3. Iterate over rows and create/update products
#             for _, row in df.iterrows():
#                 try:
#                     category_name = str(row.get('category_name', '')).strip()
#                     product_name = str(row.get('product_name', '')).strip()

#                     if not category_name or not product_name:
#                         errors += 1
#                         continue

#                     # Get or create Category
#                     category, _ = Category.objects.get_or_create(name=category_name)

#                     # Extract pricing and stock numbers safely
#                     price = float(row.get('price', 0))
#                     discounted_price = float(row.get('discounted_price')) if pd.notna(row.get('discounted_price')) and row.get('discounted_price') != '' else None
#                     stock_qty = int(row.get('available_quantity', 0)) if pd.notna(row.get('available_quantity')) else 0

#                     # Create or update Product
#                     product, created = Product.objects.update_or_create(
#                         name=product_name,
#                         defaults={
#                             'category': category,
#                             'brand': str(row.get('brand', '')) if pd.notna(row.get('brand')) else '',
#                             'unit': str(row.get('unit', '1 unit')) if pd.notna(row.get('unit')) else '1 unit',
#                             'price': price,
#                             'discounted_price': discounted_price,
#                             'image_url': str(row.get('image_url', '')) if pd.notna(row.get('image_url')) else '',
#                             'description': str(row.get('description', '')) if pd.notna(row.get('description')) else '',
#                         }
#                     )

#                     # Update Inventory
#                     Inventory.objects.update_or_create(
#                         product=product,
#                         defaults={'available_quantity': stock_qty}
#                     )

#                     success += 1

#                 except Exception as row_err:
#                     errors += 1

#             # 4. Finalize Job Status
#             job.status = 'completed' if errors == 0 else 'failed' if success == 0 else 'completed'
#             job.success_count = success
#             job.error_count = errors
#             job.save()

#             messages.success(request, f"Import finished! {success} products added/updated, {errors} errors.")

#         except Exception as e:
#             job.status = 'failed'
#             job.error_count = job.total_rows if job.total_rows > 0 else 1
#             job.save()
#             messages.error(request, f"Failed to process file: {str(e)}")

#         return redirect('bulk_import')

#     # GET Request: Display recent import jobs
#     import_jobs = BulkImportJob.objects.all().order_by('-created_at')[:10]
#     return render(request, 'bulk_import.html', {'import_jobs': import_jobs})


# @login_required
# def manage_staff(request):
#     """View and reassign staff user roles."""
#     if request.user.role not in ['admin', 'owner'] and not request.user.is_superuser:
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
#     if request.user.role not in ['employee', 'manager', 'admin', 'owner'] and not request.user.is_superuser:
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
#     if request.user.role not in ['employee', 'manager', 'admin', 'owner'] and not request.user.is_superuser:
#         raise PermissionDenied

#     if request.method == 'POST':
#         item_id = request.POST.get('item_id')
#         action = request.POST.get('action')
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
#     if request.user.role not in ['admin', 'owner'] and not request.user.is_superuser:
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
#     """Security audit log trail."""
#     if request.user.role not in ['admin', 'owner'] and not request.user.is_superuser:
#         raise PermissionDenied

#     logs = AuditLog.objects.select_related('user').all().order_by('-created_at')[:50]
#     return render(request, 'audit_logs.html', {'audit_logs': logs})











# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# import json

# from .models import Product, Category, Order, OrderItem, Address, Inventory

# # ==========================================
# # CART HELPER FUNCTIONS & API VIEWS
# # ==========================================

# def _get_cart(request):
#     """Retrieve or initialize session cart."""
#     return request.session.get('cart', {})


# from django.shortcuts import render, redirect, get_object_or_404
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST
# from .models import Product
# from django.http import JsonResponse
# from django.views.decorators.http import require_POST

# @require_POST
# def add_to_cart(request):
#     product_id = request.POST.get('product_id')
#     try:
#         quantity = int(request.POST.get('quantity', 1))
#     except (ValueError, TypeError):
#         quantity = 1

#     if not product_id:
#         return JsonResponse({'status': 'error', 'message': 'Missing product ID'}, status=400)

#     # Initialize cart dictionary in session
#     cart = request.session.get('cart', {})
#     product_id_str = str(product_id)

#     if product_id_str in cart:
#         cart[product_id_str]['quantity'] += quantity
#     else:
#         cart[product_id_str] = {'quantity': quantity}

#     # Force session persistence
#     request.session['cart'] = cart
#     request.session.modified = True

#     # Total quantity across all cart items
#     total_count = sum(item['quantity'] for item in cart.values())

#     return JsonResponse({
#         'status': 'success',
#         'cart_count': total_count
#     })

# def cart(request):
#     session_cart = request.session.get('cart', {})
#     cart_items = []
#     subtotal = 0

#     if session_cart:
#         # Convert keys to integers for Django ORM lookup
#         product_ids = [int(pid) for pid in session_cart.keys() if pid.isdigit()]
#         products = Product.objects.filter(id__in=product_ids)
#         product_map = {p.id: p for p in products}

#         for pid_str, item in session_cart.items():
#             if not pid_str.isdigit():
#                 continue
#             pid = int(pid_str)
#             if pid in product_map:
#                 product = product_map[pid]
#                 qty = item['quantity']
#                 unit_price = product.get_final_price()
#                 item_total = unit_price * qty
#                 subtotal += item_total

#                 cart_items.append({
#                     'product': product,
#                     'quantity': qty,
#                     'unit_price': unit_price,
#                     'total_price': item_total,
#                 })

#     # Delivery calculation: Free above ₹100, otherwise ₹29
#     delivery_fee = 29 if (0 < subtotal < 100) else 0
#     grand_total = subtotal + delivery_fee

#     context = {
#         'cart_items': cart_items,
#         'subtotal': subtotal,
#         'delivery_fee': delivery_fee,
#         'grand_total': grand_total,
#     }
#     return render(request, 'cart.html', context)


# def update_cart_quantity(request):
#     """Update or remove specific item in cart."""
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         product_id = str(data.get('product_id'))
#         action = data.get('action') # 'increase', 'decrease', or 'remove'

#         cart = request.session.get('cart', {})

#         if product_id in cart:
#             if action == 'increase':
#                 cart[product_id]['quantity'] += 1
#             elif action == 'decrease':
#                 cart[product_id]['quantity'] -= 1
#                 if cart[product_id]['quantity'] <= 0:
#                     del cart[product_id]
#             elif action == 'remove':
#                 del cart[product_id]

#             request.session['cart'] = cart

#         total_items = sum(item['quantity'] for item in cart.values())
#         return JsonResponse({'status': 'success', 'cart_count': total_items})

#     return JsonResponse({'status': 'error'}, status=400)


# # ==========================================
# # CHECKOUT & ORDER PLACEMENT
# # ==========================================

# @login_required
# def checkout(request):
#     """Checkout view to select delivery address and confirm order."""
#     cart_data = _get_cart(request)
#     if not cart_data:
#         messages.warning(request, "Your cart is empty.")
#         return redirect('product_list')

#     user_addresses = Address.objects.filter(user=request.user)

#     if request.method == 'POST':
#         address_id = request.POST.get('address_id')
#         payment_method = request.POST.get('payment_method', 'COD')
#         delivery_mode = request.POST.get('delivery_mode', 'instant')

#         address = get_object_or_404(Address, pk=address_id, user=request.user)

#         # Calculate totals
#         subtotal = 0
#         items_to_create = []

#         for prod_id, item in cart_data.items():
#             product = Product.objects.get(pk=prod_id)
#             unit_price = product.discounted_price or product.price
#             item_total = unit_price * item['quantity']
#             subtotal += item_total
#             items_to_create.append((product, item['quantity'], unit_price))

#         delivery_fee = 29 if subtotal < 500 else 0
#         total_amount = subtotal + delivery_fee

#         # Create Order
#         order = Order.objects.create(
#             user=request.user,
#             address=address,
#             delivery_mode=delivery_mode,
#             payment_method=payment_method,
#             total_amount=total_amount,
#             order_status='pending_acceptance'
#         )

#         # Create OrderItems
#         for product, qty, price in items_to_create:
#             OrderItem.objects.create(
#                 order=order,
#                 product=product,
#                 quantity=qty,
#                 unit_price=price,
#                 total_price=price * qty
#             )

#         # Clear session cart
#         request.session['cart'] = {}

#         messages.success(request, f"Order #{order.id} placed successfully!")
#         return redirect('order_success', order_id=order.id)

#     return render(request, 'checkout.html', {'addresses': user_addresses, 'cart_data': cart_data})


# @login_required
# def order_success(request, order_id):
#     """Order confirmation page."""
#     order = get_object_or_404(Order, pk=order_id, user=request.user)
#     return render(request, 'order_success.html', {'order': order})


# import csv
# from django.http import HttpResponse
# from django.contrib.auth.decorators import login_required

# @login_required
# def download_sample_import(request):
#     """Generates and serves a sample CSV file for bulk product uploads."""
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="cnc_product_import_sample.csv"'

#     writer = csv.writer(response)
#     # Header Row
#     writer.writerow(['category_name', 'product_name', 'brand', 'unit', 'price', 'discounted_price', 'available_quantity', 'image_url', 'description'])
    
#     # Sample Rows
#     writer.writerow(['Dairy & Eggs', 'Amul Taaza T-Special Milk', 'Amul', '500 ml', '27.00', '', '50', 'https://via.placeholder.com/300', 'Pasteurised toned milk'])
#     writer.writerow(['Snacks', 'Lays Classic Salted Chips', 'Lays', '50 g', '20.00', '18.00', '100', 'https://via.placeholder.com/300', 'Crispy salted potato chips'])

#     return response
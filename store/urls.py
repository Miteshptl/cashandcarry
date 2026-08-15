    # path('', views.home, name='home'),
    # path('categories/', views.category_list, name='category_list'),
    # path('products/', views.product_list, name='product_list'),
    # path('products/<int:pk>/', views.product_detail, name='product_detail'),
    # path('cart/', views.cart, name='cart'),
    # path('refund-request/', views.refund_request, name='refund'),
    # path('privacy-policy/', views.privacy_policy, name='privacy'),
    # path('terms/', views.terms_and_conditions, name='terms'),
    # path('refunds-policy/', views.refunds_policy, name='refunds_policy'),
    # path('returns/', views.returns_policy, name='returns'),
    # path('about/', views.about_us, name='about'),
    # path('shipping_policy/', views.shipping_policy, name='shipping_policy'),
    # path('contact/', views.contact, name='contact'),
    # path('profile/', views.profile, name='profile'),
    # path('dashboard/', views.dashboard, name='dashboard'),
    # path('manage/inventory/', views.manage_inventory, name='manage_inventory'),
    # path('manage/prices/', views.manage_prices, name='manage_prices'),
    # path('manage/coupons/', views.manage_coupons, name='manage_coupons'),
    # path('manage/bulk-import/', views.bulk_import, name='bulk_import'),
    # path('manage/staff/', views.manage_staff, name='manage_staff'),
    # path('manage/live-orders/', views.live_orders, name='live_orders'),
    # path('manage/item-picking/', views.item_picking, name='item_picking'),
    # path('manage/store-settings/', views.store_settings, name='store_settings'),
    # path('manage/audit-logs/', views.audit_logs, name='audit_logs'),

from django.urls import path
from . import views

urlpatterns = [
    # ==========================================
    # Public & Customer Storefront
    # ==========================================
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart & Checkout
    path('cart/', views.cart, name='cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # User Profile & Orders
    path('profile/', views.profile, name='profile'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),

    # Static / Legal Pages
    path('about/', views.about_us, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy-policy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_and_conditions, name='terms'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('returns/', views.returns_policy, name='returns'),
    path('refunds-policy/', views.refunds_policy, name='refunds_policy'),
    path('refund-request/', views.refund_request, name='refund'),

    # ==========================================
    # Authentication Routes
    # ==========================================
    path('login/', views.login_view, name='login'),
    path('accounts/login/', views.login_view),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ==========================================
    # Internal Staff & Operations Dashboard
    # ==========================================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/refunds/', views.manage_refunds, name='manage_refunds'),
    path('dashboard/staff/', views.manage_staff, name='staff_management'),

    # Category Management (Staff)
    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/add-category/', views.add_category, name='add_category'),
    path('manage/edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('manage/delete-category/<int:category_id>/', views.delete_category, name='delete_category'),

    # Catalog & Inventory Tools (Staff)
    path('manage/add-product/', views.add_product, name='add_product'),
    path('manage/inventory/', views.manage_inventory, name='manage_inventory'),
    path('manage/prices/', views.manage_prices, name='manage_prices'),
    path('manage/coupons/', views.manage_coupons, name='manage_coupons'),
    path('manage/bulk-import/', views.bulk_import, name='bulk_import'),
    path('bulk-import/download-sample/', views.download_sample_import, name='download_sample_import'),

    # Operations & Fulfillment (Staff)
    path('manage/live-orders/', views.live_orders, name='live_orders'),
    path('manage/item-picking/', views.item_picking, name='item_picking'),
    path('manage/staff/', views.manage_staff, name='manage_staff'),
    path('manage/store-settings/', views.store_settings, name='store_settings'),
    path('manage/audit-logs/', views.audit_logs, name='audit_logs'),
]
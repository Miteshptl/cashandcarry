from django.urls import path
from . import views

urlpatterns = [
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


# Public & Customer Pages
    path('', views.home, name='home'),
    path('categories/', views.category_list, name='category_list'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('refund-request/', views.refund_request, name='refund'),
    path('privacy-policy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_and_conditions, name='terms'),
    path('refunds-policy/', views.refunds_policy, name='refunds_policy'),
    path('returns/', views.returns_policy, name='returns'),
    path('shipping-policy/', views.shipping_policy, name='shipping_policy'),
    path('about/', views.about_us, name='about'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('bulk-import/download-sample/', views.download_sample_import, name='download_sample_import'),


    # Cart Routes
    path('cart/', views.cart, name='cart'),
    path('cart/update/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    
    # Checkout Flow
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),

    # Internal Management Pages
    path('manage/add-category/', views.add_category, name='add_category'),
    path('manage/add-product/', views.add_product, name='add_product'),
    path('manage/inventory/', views.manage_inventory, name='manage_inventory'),
    path('manage/prices/', views.manage_prices, name='manage_prices'),
    path('manage/coupons/', views.manage_coupons, name='manage_coupons'),
    path('manage/bulk-import/', views.bulk_import, name='bulk_import'),
    path('manage/staff/', views.manage_staff, name='manage_staff'),
    path('manage/live-orders/', views.live_orders, name='live_orders'),
    path('manage/item-picking/', views.item_picking, name='item_picking'),
    path('manage/store-settings/', views.store_settings, name='store_settings'),
    path('manage/audit-logs/', views.audit_logs, name='audit_logs'),

    # 👈 Admin & Staff Dashboard Routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/live-orders/', views.live_orders, name='live_orders'),
    path('dashboard/refunds/', views.manage_refunds, name='manage_refunds'),

    path('register/', views.register, name='register'),
    path('accounts/login/', views.user_login, name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('logout/', views.user_logout, name='logout'),
]


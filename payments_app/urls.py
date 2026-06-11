from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<int:order_id>/', views.payment_page, name='payment_page'),
    path('jazzcash/<int:order_id>/', views.jazzcash_payment, name='jazzcash_payment'),
    path('easypaisa/<int:order_id>/', views.easypaisa_payment, name='easypaisa_payment'),
    path('cod/<int:order_id>/', views.cod_confirm, name='cod_confirm'),
    path('success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:order_id>/', views.payment_failed, name='payment_failed'),
]
from django.urls import path
from . import views

urlpatterns = [
    path("create-customer/", views.CreateBitnobCustomer.as_view(), name="create_customer"),
    path("create-payment/", views.CreatePaymentPlan.as_view(), name="create_payment"),
    path("payment-schedules/", views.PaymentScheduleListView.as_view(), name="payment_schedules_list"),
    path("payment-schedules/<uuid:schedule_id>/", views.PaymentScheduleDetailView.as_view(), name="payment_schedule_detail"),
    path("webhook/", views.bitnob_webhook, name="bitnob_webhook"),
    path("initiate-payout/", views.InitiatePayout.as_view(), name="initiate_payout"),
    path("receiver-progress/<int:receiver_id>/", views.get_schedule_progress, name="receiver_progress"),
]

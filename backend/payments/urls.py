from django.urls import path
from . import views

urlpatterns = [
    path("create-customer/", views.CreateBitnobCustomer.as_view(), name="create_customer"),
    path("create-payment/", views.CreatePaymentPlan.as_view(), name="create_payment"),
    path("payment-schedules/", views.PaymentScheduleListView.as_view(), name="payment_schedules_list"),
    path("payment-schedules/<uuid:schedule_id>/", views.PaymentScheduleDetailView.as_view(), name="payment_schedule_detail"),
    path("payment-schedules/<uuid:schedule_id>/fund/", views.CreateUSDTDepositView.as_view(), name="fund_schedule"),
    path("payment-schedules/<uuid:schedule_id>/funding-status/", views.get_funding_status, name="funding_status"),
    path("webhook/", views.bitnob_webhook, name="bitnob_webhook"),
    path("initiate-payout/", views.InitiatePayout.as_view(), name="initiate_payout"),
    path("receiver-progress/<int:receiver_id>/", views.get_schedule_progress, name="receiver_progress"),
    path("schedules/<uuid:schedule_id>/fund-usdt/", views.CreateUSDTDepositView.as_view(), name="fund-usdt-legacy"),
    path("schedules/<uuid:schedule_id>/funding-status/", views.get_funding_status, name="funding_status_legacy"),
    path("fund-transactions/<uuid:fund_transaction_id>/confirm/", views.manual_fund_confirmation, name="manual_fund_confirmation"),
    path("test/simulate-webhook/", views.test_simulate_webhook, name="test_simulate_webhook"),
    path("trigger-scheduled-payments/", views.trigger_scheduled_payments, name="trigger_scheduled_payments"),
    path("scheduled-payments-status/", views.get_scheduled_payments_status, name="scheduled_payments_status"),
    path("test/create-schedule/", views.create_test_schedule, name="create_test_schedule"),
    path("test/create-5min-payment/", views.create_5min_test_payment, name="create_5min_test_payment"),
    path("test/bitnob-api-status/", views.check_bitnob_api_status, name="check_bitnob_api_status"),
    path("test/check-payment-timing/<int:receiver_id>/", views.check_payment_timing, name="check_payment_timing"),
]

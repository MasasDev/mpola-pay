# 5-Minute Interval Payment Testing with Bitnob API

This document explains how to test the 5-minute interval payment functionality that integrates with the Bitnob API.

## Overview

The system now supports automatic payments at 5-minute intervals with full Bitnob API integration. When a payment is due, the system will:

1. **Lookup Mobile Number** - Validate the recipient's mobile money account
2. **Create Invoice** - Generate a payment request through Bitnob
3. **Process Payment** - Execute the payment to the mobile money account
4. **Handle Webhooks** - Receive status updates from Bitnob

## API Endpoints

### 1. Check Bitnob API Status
```bash
GET /api/test/bitnob-api-status/
```
Checks connectivity and configuration with the Bitnob API.

### 2. Create Basic 5-Minute Schedule
```bash
POST /api/test/create-schedule/
Content-Type: application/json

{
  "frequency": "test_5min"
}
```

### 3. Create 5-Minute Schedule with Immediate Payment
```bash
POST /api/test/create-5min-payment/
```
This endpoint will:
- Create a new customer and payment schedule
- Set up a receiver with Uganda mobile number
- Fund the schedule automatically
- Immediately trigger a Bitnob API payment
- Return detailed API call results

### 4. Check Payment Timing
```bash
POST /api/test/check-payment-timing/{receiver_id}/
```

### 5. Trigger All Scheduled Payments
```bash
POST /api/trigger-scheduled-payments/
```

### 6. Check Scheduled Payments Status
```bash
GET /api/scheduled-payments-status/
```

## Testing Workflow

### Option 1: Using the Test Script
```bash
cd backend
python test_5min_bitnob_payments.py
```

### Option 2: Manual Testing

1. **Check API Status**
   ```bash
   curl -X GET http://localhost:8000/api/test/bitnob-api-status/
   ```

2. **Create 5-Minute Payment Test**
   ```bash
   curl -X POST http://localhost:8000/api/test/create-5min-payment/ \
        -H "Content-Type: application/json"
   ```

3. **Wait 5 minutes, then trigger next payment**
   ```bash
   curl -X POST http://localhost:8000/api/trigger-scheduled-payments/ \
        -H "Content-Type: application/json"
   ```

4. **Check status**
   ```bash
   curl -X GET http://localhost:8000/api/scheduled-payments-status/
   ```

## What Happens During a 5-Minute Payment

1. **Schedule Creation**
   - Customer: `test_5min_{random}@example.com`
   - Phone: Valid Uganda format (`77{7-digits}`)
   - Amount: 200 UGX per installment
   - Frequency: Every 5 minutes

2. **Automatic Funding**
   - Schedule is pre-funded with 2030 UGX
   - Includes 1.5% processing fee

3. **Bitnob API Calls**
   - **Mobile Lookup**: `GET /mobile/lookup` (optional, skipped for Uganda)
   - **Create Invoice**: `POST /mobile-payments/initiate`
   - **Process Payment**: `POST /payouts/mobile`

4. **Transaction Tracking**
   - Creates `MobileTransaction` record
   - Status progression: `pending` → `processing` → `success`
   - Updated via Bitnob webhooks

5. **Next Payment**
   - Scheduled automatically for 5 minutes later
   - Processed by Celery background tasks or manual trigger

## Supported Frequencies

The system supports these test frequencies:
- `test_30sec` - Every 30 seconds
- `test_2min` - Every 2 minutes  
- `test_5min` - Every 5 minutes
- `hourly` - Every hour
- `daily` - Every day
- `weekly` - Every week
- `monthly` - Every month

## Configuration

### Bitnob API Settings
```python
# In settings.py
BITNOB_API_KEY = 'sk.3a846ff0dfb8.7e7ddae08f05636a83433470b'

# API endpoints now use sandbox:
BITNOB_BASE = "https://sandboxapi.bitnob.co/api/v1"
```

### Phone Number Format
- Country Code: `256` (Uganda)
- Phone Format: `77{7-digits}` (e.g., `770123456`)
- Full Format: `+256770123456`

## Troubleshooting

### Common Issues

1. **IP Restrictions (403 Error)**
   - Solution: Now using sandbox API which has fewer restrictions
   - Check: `GET /api/test/bitnob-api-status/`

2. **Payment Timing Issues**
   - Check: `POST /api/test/check-payment-timing/{receiver_id}/`
   - Solution: Payments are only processed when due based on frequency

3. **Insufficient Funds**
   - Check: Schedule is automatically funded in test mode
   - Verify: `GET /api/payment-schedules/{schedule_id}/funding-status/`

### Error Handling

The system now includes comprehensive error handling:
- Network errors return HTTP 503
- API errors return HTTP 400 with user-friendly messages
- All responses include detailed error information

## Example Response

```json
{
  "message": "5-minute test schedule created and first payment initiated successfully!",
  "success": true,
  "bitnob_api_calls": {
    "lookup": {"status": true, "message": "Lookup skipped for Uganda"},
    "invoice": {"status": true, "data": {"reference": "abc123", "paymentRequest": "..."}},
    "payment": {"status": true, "data": {"transaction_id": "xyz789"}}
  },
  "schedule": {
    "id": "uuid-here",
    "title": "5-Minute Bitnob Test Schedule",
    "frequency": "test_5min",
    "next_payment_date": "2025-07-25T09:25:00Z"
  },
  "transaction": {
    "id": 123,
    "reference": "abc123",
    "amount": "200.0",
    "installment_number": 1,
    "status": "processing"
  },
  "next_steps": [
    "Transaction is now processing with Bitnob",
    "Webhook will update status to 'success' when payment completes",
    "Next payment will be due in 5 minutes",
    "Use the trigger_scheduled_payments endpoint to process future payments"
  ]
}
```

## Monitoring

### Real-time Monitoring
- Check logs for Bitnob API responses
- Monitor webhook calls at `/api/webhook/`
- Track transaction status changes

### Database Records
- `PaymentSchedule` - Contains schedule configuration
- `MobileReceiver` - Contains recipient details
- `MobileTransaction` - Contains payment attempts
- `FundTransaction` - Contains funding records

## Production Considerations

When moving to production:
1. Change `BITNOB_BASE` to production API
2. Use real customer data and phone numbers
3. Implement proper error notifications
4. Set up proper webhook URL for status updates
5. Configure Celery for background task processing

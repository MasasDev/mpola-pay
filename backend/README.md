# Mpola Payment Management System

A Django-based payment management system that integrates with Bitnob API for mobile payments and installment scheduling.

## Features

- Customer management with Bitnob integration
- Payment schedule creation with multiple receivers
- Mobile money transactions with installment tracking
- Webhook handling for payment status updates
- Progress tracking and reporting

## API Endpoints

### Base URL
```
http://localhost:8000/
```

## Getting Started

### Prerequisites
- Python 3.8+
- Django 5.2+
- Redis (for Celery)
- Bitnob API credentials

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd mpola
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables
```bash
# Add to your settings.py or .env file
BITNOB_API_KEY=your_bitnob_api_key_here
```

4. Run migrations
```bash
python manage.py migrate
```

5. Start the development server
```bash
python manage.py runserver
```

## Postman API Testing Guide

### Step 1: Set up Environment Variables in Postman

Create a new environment in Postman with the following variables:

```
base_url: http://localhost:8000
customer_email: test@example.com
customer_bitnob_id: (will be set from response)
payment_schedule_id: (will be set from response)
receiver_id: (will be set from response)
```

### Step 2: Create a Bitnob Customer

**POST** `{{base_url}}/create-customer/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "email": "john.doe@example.com",
    "firstName": "John",
    "lastName": "Doe",
    "phone": "+2348123456789",
    "countryCode": "NG"
}
```

**Expected Response:**
```json
{
    "message": "Customer created",
    "bitnob_id": "bitnob_customer_id_here"
}
```

**Post-Response Script:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("customer_bitnob_id", response.bitnob_id);
    pm.environment.set("customer_email", "john.doe@example.com");
}
```

### Step 3: Create a Payment Schedule

**POST** `{{base_url}}/create-payment/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "email": "{{customer_email}}",
    "title": "Monthly Family Support",
    "description": "Monthly payments to family members",
    "frequency": "monthly",
    "receivers": [
        {
            "name": "Jane Doe",
            "phone": "+2348123456790",
            "countryCode": "NG",
            "amountPerInstallment": 50000,
            "numberOfInstallments": 12
        },
        {
            "name": "Mike Smith",
            "phone": "+2348123456791",
            "countryCode": "NG",
            "amountPerInstallment": 30000,
            "numberOfInstallments": 6
        }
    ]
}
```

**Expected Response:**
```json
{
    "message": "Payment schedule created successfully",
    "payment_schedule": {
        "id": "uuid-here",
        "title": "Monthly Family Support",
        "status": "active",
        "total_amount": "780000.00",
        "frequency": "monthly",
        "total_receivers": 2,
        "progress_percentage": 0.0
    },
    "receivers": [
        {
            "id": 1,
            "name": "Jane Doe",
            "phone": "+2348123456790",
            "total_amount": "600000.00",
            "installments": 12
        },
        {
            "id": 2,
            "name": "Mike Smith",
            "phone": "+2348123456791",
            "total_amount": "180000.00",
            "installments": 6
        }
    ]
}
```

**Post-Response Script:**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.environment.set("payment_schedule_id", response.payment_schedule.id);
    pm.environment.set("receiver_id", response.receivers[0].id);
}
```

### Step 4: List Payment Schedules

**GET** `{{base_url}}/payment-schedules/`

**Query Parameters (Optional):**
- `customer_email`: Filter by customer email
- `status`: Filter by status (active, completed, paused, cancelled)

**Example with filters:**
`{{base_url}}/payment-schedules/?customer_email={{customer_email}}&status=active`

**Expected Response:**
```json
{
    "payment_schedules": [
        {
            "id": "uuid-here",
            "title": "Monthly Family Support",
            "description": "Monthly payments to family members",
            "status": "active",
            "total_amount": "780000.00",
            "frequency": "monthly",
            "start_date": "2025-07-24T12:00:00Z",
            "created_at": "2025-07-24T12:00:00Z",
            "total_receivers": 2,
            "total_transactions": 0,
            "completed_transactions": 0,
            "progress_percentage": 0.0,
            "is_completed": false,
            "customer_name": "John Doe"
        }
    ],
    "count": 1
}
```

### Step 5: Get Payment Schedule Details

**GET** `{{base_url}}/payment-schedules/{{payment_schedule_id}}/`

**Expected Response:**
```json
{
    "payment_schedule": {
        "id": "uuid-here",
        "title": "Monthly Family Support",
        "status": "active",
        "total_amount": "780000.00",
        "progress_percentage": 0.0
    },
    "receivers": [
        {
            "id": 1,
            "name": "Jane Doe",
            "phone": "+2348123456790",
            "amount_per_installment": "50000.00",
            "number_of_installments": 12,
            "completed_installments": 0,
            "progress_percentage": 0.0,
            "transactions": []
        }
    ]
}
```

### Step 6: Update Payment Schedule

**PATCH** `{{base_url}}/payment-schedules/{{payment_schedule_id}}/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "status": "paused",
    "title": "Updated Monthly Family Support",
    "description": "Updated description for the payment schedule"
}
```

**Expected Response:**
```json
{
    "message": "Payment schedule updated successfully",
    "payment_schedule": {
        "id": "uuid-here",
        "title": "Updated Monthly Family Support",
        "status": "paused",
        "total_amount": "780000.00"
    }
}
```

### Step 7: Initiate a Payout

**POST** `{{base_url}}/initiate-payout/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "countryCode": "NG",
    "phone": "+2348123456790",
    "senderName": "John Doe",
    "amount": "50000",
    "customerEmail": "{{customer_email}}"
}
```

**Expected Response:**
```json
{
    "reference": "bitnob_reference_here",
    "paymentRequest": "payment_request_data",
    "transactionId": 1
}
```

**Post-Response Script:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("transaction_reference", response.reference);
    pm.environment.set("transaction_id", response.transactionId);
}
```

### Step 8: Get Receiver Progress

**GET** `{{base_url}}/balance-progress/{{receiver_id}}/`

**Expected Response:**
```json
{
    "receiver_id": 1,
    "receiver_name": "Jane Doe",
    "receiver_phone": "+2348123456790",
    "total_installments": 12,
    "completed_installments": 1,
    "pending_installments": 0,
    "failed_installments": 0,
    "total_amount": "600000.00",
    "completed_amount": "50000.00",
    "progress_percentage": 8.33,
    "transactions": [
        {
            "id": 1,
            "installment_number": 1,
            "amount": "50000.00",
            "status": "success",
            "sent_at": "2025-07-24T12:30:00Z"
        }
    ]
}
```

### Step 9: Webhook Testing (Simulate Bitnob Callback)

**POST** `{{base_url}}/webhook/`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON) - Success:**
```json
{
    "event": "mobilepayment.settlement.success",
    "reference": "{{transaction_reference}}"
}
```

**Body (JSON) - Failure:**
```json
{
    "event": "mobilepayment.settlement.failed",
    "reference": "{{transaction_reference}}"
}
```

**Expected Response:**
```json
{
    "status": "received"
}
```

## Postman Collection Setup

### Environment Variables Summary
```
base_url: http://localhost:8000
customer_email: (set from customer creation)
customer_bitnob_id: (set from customer creation)
payment_schedule_id: (set from schedule creation)
receiver_id: (set from schedule creation)
transaction_reference: (set from payout initiation)
transaction_id: (set from payout initiation)
```

### Recommended Test Flow

1. **Create Customer** → Sets `customer_email` and `customer_bitnob_id`
2. **Create Payment Schedule** → Sets `payment_schedule_id` and `receiver_id`
3. **List Payment Schedules** → Verify creation
4. **Get Schedule Details** → Verify complete data
5. **Initiate Payout** → Sets `transaction_reference` and `transaction_id`
6. **Webhook Success** → Update transaction status
7. **Get Receiver Progress** → Verify updated progress
8. **Update Schedule** → Test schedule management

## Error Handling

Common error responses:

**400 Bad Request:**
```json
{
    "error": "Validation error message",
    "field_errors": {
        "field_name": ["Error message"]
    }
}
```

**404 Not Found:**
```json
{
    "error": "Customer not found"
}
```

**500 Internal Server Error:**
```json
{
    "error": "Internal server error",
    "detail": "Error details"
}
```

## Database Models

### PaymentSchedule
- Groups multiple receivers under one payment plan
- Tracks overall progress and status
- Links to customer

### MobileReceiver
- Individual recipient within a payment schedule
- Defines installment amount and count
- Tracks individual progress

### MobileTransaction
- Individual payment transaction
- Links to receiver and installment number
- Tracks payment status and references

## Development Notes

- All monetary amounts are in kobo (multiply by 100 for Bitnob API)
- UUIDs are used for payment schedule IDs for security
- Webhook endpoint handles Bitnob payment status updates
- Progress percentages are calculated automatically

## Support

For API issues or questions, please check:
1. Django logs for server errors
2. Bitnob API documentation for payment-related issues
3. Database migrations are up to date

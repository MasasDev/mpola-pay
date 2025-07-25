# Mpola Payment API - Postman Collection

This updated Postman collection provides comprehensive testing for the Mpola Payment Management API with proper country code formatting (WITHOUT plus signs).

## Files

- `Mpola_API_Collection_Updated.postman_collection.json` - Main API collection
- `Mpola_Development_Updated.postman_environment.json` - Environment variables

## Key Changes

### Country Code Format
- ✅ **CORRECT**: `"countryCode": "256"` (for Uganda)
- ✅ **CORRECT**: `"countryCode": "234"` (for Nigeria)  
- ✅ **CORRECT**: `"countryCode": "254"` (for Kenya)
- ❌ **INCORRECT**: `"countryCode": "+256"` (with plus sign)

The API now automatically strips any plus signs from country codes, so both formats work, but the standard is without plus signs.

## Environment Variables

The collection uses these environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `base_url` | API base URL | `http://localhost:8000` |
| `customer_email` | Test customer email | `john.doe@example.com` |
| `customer_bitnob_id` | Customer ID from Bitnob | Auto-set by requests |
| `payment_schedule_id` | Payment schedule UUID | Auto-set by requests |
| `receiver_id` | Receiver ID | Auto-set by requests |
| `transaction_id` | Transaction ID | Auto-set by requests |
| `payment_reference` | Payment reference | Auto-set by requests |
| `fund_transaction_reference` | Fund transaction reference | Auto-set by requests |

## API Endpoints Organized by Category

### 1. Customer Management
- **Create Customer** - Creates a new Bitnob customer

### 2. Payment Schedule Management
- **Create Payment Schedule** - Creates a payment plan with multiple receivers
- **List All Payment Schedules** - Gets all payment schedules
- **List Payment Schedules by Customer** - Filters by customer email
- **Get Payment Schedule Details** - Get detailed schedule info with receivers
- **Update Payment Schedule Status** - Updates schedule status/details

### 3. Funding Management
- **Create USDT Deposit (TRON)** - Creates USDT deposit address on TRON network
- **Create USDT Deposit (Ethereum)** - Creates USDT deposit address on Ethereum network
- **Get Funding Status** - Check funding status of a payment schedule
- **Manual Fund Confirmation** - Admin endpoint to manually confirm funding

### 4. Payment Execution
- **Initiate Payout** - Send money to a specific receiver
- **Get Receiver Progress** - Check payment progress for a receiver

### 5. Scheduled Payments Management
- **Trigger Scheduled Payments (All)** - Process all due payments
- **Trigger Scheduled Payments (Specific)** - Process payments for specific schedule
- **Get Scheduled Payments Status** - Get overview of scheduled payment status

### 6. Webhooks & Testing
- **Bitnob Webhook (Mobile Payment Success)** - Simulate successful payment webhook
- **Bitnob Webhook (Mobile Payment Failed)** - Simulate failed payment webhook
- **Bitnob Webhook (Fund Transaction Success)** - Simulate successful funding webhook
- **Test Simulate Webhook** - Test endpoint for webhook simulation

### 7. Complete Workflow Examples
- **Example: Create Customer with Uganda Phone** - Example with Uganda phone format
- **Example: Create Customer with Nigeria Phone** - Example with Nigeria phone format
- **Example: Payment Schedule with Mixed Countries** - Multi-country payment schedule

## Usage Instructions

### 1. Import Collection
1. Open Postman
2. Click "Import"
3. Select `Mpola_API_Collection_Updated.postman_collection.json`
4. Select `Mpola_Development_Updated.postman_environment.json`

### 2. Set Environment
1. Select "Mpola Development (Updated)" environment
2. Ensure `base_url` is set to your server URL (default: `http://localhost:8000`)

### 3. Run Complete Workflow
1. **Create Customer** - Run first to set up customer variables
2. **Create Payment Schedule** - Creates schedule and sets receiver variables
3. **Create USDT Deposit** - Generate funding address
4. **Manual Fund Confirmation** (or wait for real USDT deposit)
5. **Initiate Payout** - Send actual payments

### 4. Monitor Progress
- Use **Get Funding Status** to check if schedule is funded
- Use **Get Receiver Progress** to monitor payment completion
- Use **Get Scheduled Payments Status** for overall system status

## Country Code Examples

### Common Country Codes (WITHOUT plus signs)
- **Uganda**: `256`
- **Nigeria**: `234` 
- **Kenya**: `254`
- **Ghana**: `233`
- **Tanzania**: `255`
- **Rwanda**: `250`
- **South Africa**: `27`
- **United States**: `1`

### Phone Number Examples
```json
{
  "phone": "700123456",
  "countryCode": "256"
}
```

## Testing Notes

1. **Environment Variables**: Many variables are auto-set by test scripts
2. **Response Validation**: Each request includes test scripts for validation
3. **Error Handling**: Failed requests log detailed error information
4. **Sequencing**: Run requests in order for best results
5. **Clean State**: Some tests may require database cleanup between runs

## Troubleshooting

### Common Issues

1. **Country Code Validation Errors**
   - Ensure country codes don't have plus signs
   - Use standard country calling codes (e.g., 256 for Uganda)

2. **Customer Not Found**
   - Run "Create Customer" first
   - Check that `customer_email` environment variable is set

3. **Schedule Not Funded**
   - Use "Manual Fund Confirmation" for testing
   - Or complete real USDT deposit process

4. **Receiver Not Found**
   - Ensure "Create Payment Schedule" ran successfully
   - Check `receiver_id` environment variable

### API Server Setup
```bash
cd backend
python manage.py runserver 8000
```

### Database Reset (if needed)
```bash
python manage.py flush
python manage.py migrate
```

## Support

For issues or questions:
1. Check the response logs in Postman console
2. Verify environment variables are set correctly
3. Ensure API server is running on correct port
4. Check database connectivity

## Version History

- **v2.0** - Updated country codes to remove plus signs, improved organization
- **v1.0** - Initial collection with basic functionality

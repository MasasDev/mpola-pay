# Frontend-Backend Harmonization

This document outlines the changes made to harmonize the frontend Angular application with the backend Django API.

## Overview

The frontend has been completely restructured to work with the real backend API instead of mock data. The main changes include:

### 1. Updated Data Models

**Before:** Simple recipient-based model with mock scheduled payments
**After:** Complete payment schedule system matching backend models

#### New Interfaces:
- `PaymentSchedule`: Main schedule entity with funding and payment tracking
- `BitnobCustomer`: Customer management 
- `Transaction`: Individual payment transactions
- `FundTransaction`: Funding/deposit transactions
- `CreatePaymentScheduleRequest`: API request structure

### 2. New Services

#### ApiService
- Centralized HTTP client for all backend API calls
- Endpoints for customers, payment schedules, payments, and funding
- Error handling and response typing

#### FundingService  
- Manages USDT deposit creation and tracking
- Funding status monitoring
- Webhook simulation for testing

#### Updated RecipientService
- Now works with payment schedules instead of individual recipients
- Real API integration for schedule management
- Observable-based data flow

#### Updated ScheduledPaymentService
- Real-time payment monitoring
- Integration with backend scheduled payment system
- Payment timing validation

### 3. Component Updates

#### Dashboard Page
- Displays real payment schedules and funding status
- Integrated payment triggering and monitoring
- Schedule management (pause/resume/fund)
- Real-time status updates

#### Schedule Payment Modal
- Complete rewrite for backend integration
- Customer creation workflow
- Multi-receiver support with validation
- Real-time cost calculation

#### Deposit Modal
- USDT deposit address generation
- Multiple network support (TRON, Ethereum, BSC, Polygon)
- Funding status tracking
- Webhook simulation for testing

### 4. Key Features

#### Payment Schedule Management
- Create schedules with multiple receivers
- Automatic processing fee calculation (1.5%)
- Phone number uniqueness validation
- Frequency options (daily, weekly, monthly, test modes)

#### Funding System
- USDT deposit integration
- Real-time funding status tracking
- Multiple blockchain network support
- Automatic funding validation

#### Payment Processing
- Schedule-based automatic payments
- Payment timing validation
- Real-time status updates
- Transaction history tracking

#### Monitoring & Analytics
- Payment schedule progress tracking
- Funding status monitoring
- Real-time alerts and notifications
- Comprehensive dashboard metrics

## API Integration

### Base URL
```typescript
private baseUrl = 'http://localhost:8000/api';
```

### Key Endpoints
- `POST /create-customer/` - Create Bitnob customer
- `POST /create-payment-plan/` - Create payment schedule
- `GET /payment-schedules/` - List payment schedules
- `POST /initiate-payout/` - Trigger payment
- `POST /payment-schedules/{id}/fund/` - Create funding deposit
- `GET /scheduled-payments-status/` - Get payment monitoring status

## Configuration Changes

### HttpClient Setup
Added `provideHttpClient` to app configuration for API calls.

### Service Dependencies
All services now properly inject and use the ApiService for backend communication.

## Error Handling

- Comprehensive error handling in all API calls
- User-friendly error messages
- Graceful fallbacks for network issues
- Toast notifications for user feedback

## Testing Features

- Test schedule creation with 30-second intervals
- Webhook simulation for funding confirmation
- Manual payment triggering
- Real-time monitoring dashboard

## Usage Examples

### Creating a Payment Schedule
```typescript
const scheduleData = {
  email: 'customer@example.com',
  title: 'Monthly Family Support',
  frequency: 'monthly',
  receivers: [
    {
      name: 'John Doe',
      phone: '+256700000001',
      countryCode: 'UG',
      amountPerInstallment: 100000,
      numberOfInstallments: 12
    }
  ]
};

this.recipientService.createPaymentSchedule(scheduleData).subscribe(result => {
  console.log('Schedule created:', result);
});
```

### Funding a Schedule
```typescript
this.fundingService.createUSDTDeposit(scheduleId, 'TRON').subscribe(result => {
  const depositAddress = result.funding_details.deposit_address;
  const usdtRequired = result.funding_details.usdt_required;
  // Display deposit instructions to user
});
```

### Monitoring Payments
```typescript
this.scheduledPaymentService.startMonitoring();
this.scheduledPaymentService.scheduledPayments$.subscribe(payments => {
  // Handle payment updates
});
```

## Future Enhancements

1. **Real-time WebSocket Integration**: Replace polling with WebSocket for real-time updates
2. **Mobile Responsiveness**: Optimize UI for mobile devices
3. **Advanced Analytics**: Add charts and detailed reporting
4. **User Management**: Add role-based access control
5. **Notification System**: Email/SMS notifications for payment events
6. **Multi-currency Support**: Support for multiple currencies beyond UGX
7. **Batch Operations**: Bulk payment processing and schedule management

## Dependencies

### New Dependencies Added
- `@angular/common/http` - HTTP client for API calls
- Observable patterns for reactive data flow

### Updated Components
All major components updated to work with real backend data instead of mock data.

## Migration Notes

- Old mock data structures have been completely replaced
- All hardcoded values now come from the backend
- Error handling is now comprehensive and user-friendly
- The application now requires the backend to be running for full functionality

This harmonization creates a production-ready frontend that fully integrates with the Django backend, providing a complete payment scheduling and management system.

// Example data structures for the Mpola Pay Simple Frontend

// Example of a Customer Creation Request
const exampleCustomerRequest = {
  email: "john.doe@example.com",
  firstName: "John",
  lastName: "Doe",
  phone: "1234567890",
  countryCode: "+1"
};

// Example of a Customer Creation Response
const exampleCustomerResponse = {
  message: "Customer created successfully",
  bitnob_id: "bitnob_customer_id_12345",
  local_id: 1
};

// Example of a Payment Schedule Creation Request
const exampleCreateRequest = {
  email: "customer@example.com",
  title: "Monthly Family Support",
  description: "Monthly payments to family members",
  frequency: "monthly",
  start_date: "2024-01-15T10:00:00Z",
  receivers: [
    {
      name: "John Doe",
      phone: "1234567890",
      countryCode: "+1",
      amountPerInstallment: 100.00,
      numberOfInstallments: 12
    },
    {
      name: "Jane Smith", 
      phone: "0987654321",
      countryCode: "+234",
      amountPerInstallment: 75.00,
      numberOfInstallments: 6
    }
  ]
};

// Example of a Payment Schedule Response
const exampleScheduleResponse = {
  id: "uuid-1234-5678",
  title: "Monthly Family Support",
  description: "Monthly payments to family members",
  frequency: "monthly",
  subtotal_amount: 1050.00,
  processing_fee: 31.50,
  total_amount: 1081.50,
  start_date: "2024-01-15T10:00:00Z",
  status: "active",
  is_funded: true,
  is_adequately_funded: false,
  total_funded_amount: 500.00,
  total_payments_made: 175.00,
  available_balance: 325.00,
  funding_shortfall: 581.50,
  next_payment_date: "2024-02-15T10:00:00Z",
  last_payment_date: "2024-01-15T10:00:00Z",
  created_at: "2024-01-01T10:00:00Z",
  customer_email: "customer@example.com",
  receivers: [
    {
      id: 1,
      name: "John Doe",
      phone: "1234567890",
      country_code: "+1",
      amount_per_installment: 100.00,
      number_of_installments: 12,
      completed_installments: 1,
      progress_percentage: 8.33,
      total_amount: 1200.00
    },
    {
      id: 2,
      name: "Jane Smith",
      phone: "0987654321", 
      country_code: "+234",
      amount_per_installment: 75.00,
      number_of_installments: 6,
      completed_installments: 1,
      progress_percentage: 16.67,
      total_amount: 450.00
    }
  ]
};

export { exampleCustomerRequest, exampleCustomerResponse, exampleCreateRequest, exampleScheduleResponse };

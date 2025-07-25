import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor to handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Log all API errors for debugging
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    });

    // Ensure error response has a consistent structure
    if (error.response?.data && typeof error.response.data === 'object') {
      // Already has structured error data
      return Promise.reject(error);
    }

    // Create structured error for network errors or malformed responses
    const structuredError = {
      ...error,
      response: {
        ...error.response,
        data: {
          error: error.message || 'Unknown error occurred',
          message: error.message || 'Unknown error occurred',
          detail: error.response?.data || 'No additional details available'
        }
      }
    };

    return Promise.reject(structuredError);
  }
);

export const customerAPI = {
  // Create a new customer
  createCustomer: (customerData) => {
    // Add mock mode for testing when backend is down
    if (process.env.REACT_APP_MOCK_MODE === 'true') {
      return new Promise((resolve) => {
        setTimeout(() => {
          resolve({
            data: {
              message: "Customer created successfully (MOCK MODE)",
              bitnob_id: `mock_${Date.now()}`,
              local_id: Math.floor(Math.random() * 1000)
            }
          });
        }, 1000);
      });
    }
    
    return api.post('/api/create-customer/', customerData);
  },

  // Get all customers (if endpoint exists)
  getCustomers: () => 
    api.get('/api/customers/'),
};

export const paymentScheduleAPI = {
  // Create a new payment schedule
  createSchedule: (scheduleData) => 
    api.post('/api/payment-schedules/', scheduleData),

  // Get all payment schedules
  getSchedules: () => 
    api.get('/api/payment-schedules/'),

  // Get a specific payment schedule
  getSchedule: (id) => 
    api.get(`/api/payment-schedules/${id}/`),

  // Update a payment schedule
  updateSchedule: (id, scheduleData) => 
    api.patch(`/api/payment-schedules/${id}/`, scheduleData),

  // Delete a payment schedule
  deleteSchedule: (id) => 
    api.delete(`/api/payment-schedules/${id}/`),

  // Fund a payment schedule (generates USDT deposit address)
  fundSchedule: (id, network = 'TRON') => 
    api.post(`/api/payment-schedules/${id}/fund/`, { network }),

  // Get funding status for a payment schedule
  getFundingStatus: (id) => 
    api.get(`/api/payment-schedules/${id}/funding-status/`),

  // Pause/Resume a payment schedule
  toggleSchedule: (id, action) => {
    const status = action === 'activate' ? 'active' : 'paused';
    return api.patch(`/api/payment-schedules/${id}/`, { status });
  },
};

export const testAPI = {
  // Create a test payment schedule with configurable frequency
  createTestSchedule: (frequency = 'test_5min') => 
    api.post('/api/test/create-schedule/', { frequency }),

  // Create a 5-minute test payment and trigger Bitnob API call
  create5MinTest: () => 
    api.post('/api/test/create-5min-payment/'),

  // Trigger scheduled payments processing
  triggerScheduledPayments: (scheduleId = null) => {
    const data = scheduleId ? { schedule_id: scheduleId } : {};
    return api.post('/api/trigger-scheduled-payments/', data);
  },

  // Get scheduled payments status
  getScheduledPaymentsStatus: () => 
    api.get('/api/scheduled-payments-status/'),

  // Check Bitnob API status
  checkBitnobApiStatus: () => 
    api.get('/api/test/bitnob-api-status/'),

  // Check payment timing for a receiver
  checkPaymentTiming: (receiverId) => 
    api.get(`/api/test/check-payment-timing/${receiverId}/`),

  // Simulate webhook for testing
  simulateWebhook: (reference, event = 'stablecoin.deposit.confirmed') => 
    api.post('/api/test/simulate-webhook/', { reference, event }),
};

export default api;

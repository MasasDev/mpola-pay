import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const customerAPI = {
  // Create a new customer
  createCustomer: (customerData) => 
    api.post('/api/create-customer/', customerData),

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

export default api;

import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { 
  BitnobCustomer, 
  PaymentSchedule, 
  Transaction, 
  FundTransaction 
} from '../interfaces/recipient';
import { 
  ScheduledPayment, 
  CreatePaymentScheduleRequest 
} from '../interfaces/scheduled-payment';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000/api';

  private httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
    })
  };

  constructor(private http: HttpClient) {}

  // Customer Management
  createCustomer(customerData: {
    email: string;
    firstName: string;
    lastName: string;
    phone: string;
    countryCode: string;
  }): Observable<any> {
    return this.http.post(`${this.baseUrl}/create-customer/`, customerData, this.httpOptions);
  }

  // Payment Schedule Management
  createPaymentSchedule(scheduleData: CreatePaymentScheduleRequest): Observable<any> {
    return this.http.post(`${this.baseUrl}/create-payment-plan/`, scheduleData, this.httpOptions);
  }

  getPaymentSchedules(customerEmail?: string, status?: string): Observable<{
    payment_schedules: ScheduledPayment[];
    count: number;
  }> {
    let url = `${this.baseUrl}/payment-schedules/`;
    const params: string[] = [];
    
    if (customerEmail) {
      params.push(`customer_email=${encodeURIComponent(customerEmail)}`);
    }
    if (status) {
      params.push(`status=${encodeURIComponent(status)}`);
    }
    
    if (params.length > 0) {
      url += '?' + params.join('&');
    }
    
    return this.http.get<{
      payment_schedules: ScheduledPayment[];
      count: number;
    }>(url, this.httpOptions);
  }

  getPaymentScheduleDetail(scheduleId: string): Observable<{
    payment_schedule: ScheduledPayment;
    receivers: any[];
  }> {
    return this.http.get<{
      payment_schedule: ScheduledPayment;
      receivers: any[];
    }>(`${this.baseUrl}/payment-schedules/${scheduleId}/`, this.httpOptions);
  }

  updatePaymentSchedule(scheduleId: string, updates: Partial<ScheduledPayment>): Observable<any> {
    return this.http.patch(`${this.baseUrl}/payment-schedules/${scheduleId}/`, updates, this.httpOptions);
  }

  // Payment Processing
  initiatePayout(payoutData: {
    receiverId: number;
    senderName: string;
  }): Observable<any> {
    return this.http.post(`${this.baseUrl}/initiate-payout/`, payoutData, this.httpOptions);
  }

  getReceiverProgress(receiverId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/schedule-progress/${receiverId}/`, this.httpOptions);
  }

  // Funding Management
  createUSDTDeposit(scheduleId: string, network: string = 'TRON'): Observable<any> {
    return this.http.post(`${this.baseUrl}/payment-schedules/${scheduleId}/fund/`, 
      { network }, this.httpOptions);
  }

  getFundingStatus(scheduleId: string): Observable<{
    schedule: any;
    funding_summary: any;
    fund_transactions: FundTransaction[];
    transaction_count: number;
  }> {
    return this.http.get<{
      schedule: any;
      funding_summary: any;
      fund_transactions: FundTransaction[];
      transaction_count: number;
    }>(`${this.baseUrl}/payment-schedules/${scheduleId}/funding-status/`, this.httpOptions);
  }

  manualFundConfirmation(fundTransactionId: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/fund-transactions/${fundTransactionId}/confirm/`, 
      {}, this.httpOptions);
  }

  // Scheduled Payments Management
  triggerScheduledPayments(scheduleId?: string): Observable<any> {
    const payload = scheduleId ? { schedule_id: scheduleId } : {};
    return this.http.post(`${this.baseUrl}/trigger-scheduled-payments/`, payload, this.httpOptions);
  }

  getScheduledPaymentsStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/scheduled-payments-status/`, this.httpOptions);
  }

  checkPaymentTiming(receiverId: number): Observable<any> {
    return this.http.get(`${this.baseUrl}/check-payment-timing/${receiverId}/`, this.httpOptions);
  }

  // Testing Endpoints
  createTestSchedule(): Observable<any> {
    return this.http.post(`${this.baseUrl}/create-test-schedule/`, {}, this.httpOptions);
  }

  simulateWebhook(reference: string, event: string = 'stablecoin.deposit.confirmed'): Observable<any> {
    return this.http.post(`${this.baseUrl}/test-simulate-webhook/`, 
      { reference, event }, this.httpOptions);
  }
}

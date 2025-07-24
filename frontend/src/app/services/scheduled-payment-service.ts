import { Injectable } from '@angular/core';
import { ScheduledPayment } from '../interfaces/scheduled-payment';
import { RecipientService } from './recipient-service';
import { AlertService } from './alert-service';

@Injectable({
  providedIn: 'root'
})
export class ScheduledPaymentService {


  constructor(private recipientService: RecipientService, private alertService: AlertService) {}
  
  public checkForDuePayments(): void {
    const now = new Date();
    const recipients = this.recipientService.getAllRecipients();

    for (const recipient of recipients) {
      for (const payment of recipient.scheduledPayments) {
        if (payment.isActive && payment.nextExecution) {
          const execTime = new Date(payment.nextExecution);
          const diff = execTime.getTime() - now.getTime();

          if (diff <= 1000 && diff > -2000) {
            this.handleDuePayment(payment);
          }
        }
      }
    }
  }

  private handleDuePayment(payment: ScheduledPayment): void {

    this.alertService.show(`Payment of ${payment.amount} to ${payment.recipientId} is due!`, 'success');

    console.log('📤 Simulating POST to backend:', {
      recipientId: payment.recipientId,
      amount: payment.amount
    });

    // You can uncomment this when you add real backend support
    // this.http.post('/api/process-payment', {
    //   recipientId: payment.recipientId,
    //   amount: payment.amount
    // }).subscribe();

    // Simulate incrementing execution count and setting next execution
    payment.totalExecutions++;

    const next = new Date(payment.nextExecution!);
    next.setDate(next.getDate() + 1); // Simulate daily schedule
    payment.nextExecution = next;
  }
}

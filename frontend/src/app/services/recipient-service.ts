import { Injectable } from '@angular/core';
import { Recipient } from '../interfaces/recipient';

@Injectable({
  providedIn: 'root'
})
export class RecipientService {

  recipients: Recipient[] = [];

  getAllRecipients(): Recipient[] {
    return this.recipients;
  }
   addRecipient(newRecipient: Recipient) {
    if (newRecipient.name && newRecipient.email) {
      const recipient: Recipient = {
        id: this.getNextId(),
        name: newRecipient.name,
        email: newRecipient.email,
        phone: newRecipient.phone,
        status: 'active',
        createdAt: new Date(),
        scheduledPayments: [],
        totalScheduled: 0
      };

      this.recipients.push(recipient);
    }
  }
  deleteRecipient(id: number) {
    this.recipients = this.recipients.filter(r => r.id !== id);
    //this.recipients.forEach(recipient => this.recalculateRecipientTotals(recipient));
  }

  private getNextId(): number {
    return Math.max(...this.recipients.map(r => r.id), 0) + 1;
  }
  recalculateRecipientTotals(recipient: Recipient) {
    const activePayments = recipient.scheduledPayments.filter(p => p.isActive);
    
    // Calculate total scheduled amount (rough estimate for next 4 cycles)
    recipient.totalScheduled = activePayments.reduce((sum, p) => sum + (p.amount * 4), 0);
    
    // Find next payment date
    if (activePayments.length > 0) {
      const nextPayments = activePayments.map(p => p.nextExecution).sort((a, b) => a.getTime() - b.getTime());
      recipient.nextPayment = nextPayments[0];
    } else {
      recipient.nextPayment = undefined;
    }
  }
  private getNextWeekday(dayOfWeek: number, time: string): Date {
    const now = new Date();
    const [hours, minutes] = time.split(':').map(Number);
    const targetDate = new Date(now);
    
    // Calculate days until next occurrence of dayOfWeek
    const daysUntilTarget = (dayOfWeek - now.getDay() + 7) % 7;
    targetDate.setDate(now.getDate() + (daysUntilTarget === 0 ? 7 : daysUntilTarget));
    targetDate.setHours(hours, minutes, 0, 0);
    
    return targetDate;
  }
}

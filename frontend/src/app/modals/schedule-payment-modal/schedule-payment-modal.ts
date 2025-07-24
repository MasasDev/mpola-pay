import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ScheduledPayment } from '../../interfaces/scheduled-payment';
import { Recipient } from '../../interfaces/recipient';
import { RecipientService } from '../../services/recipient-service';
import { AlertService } from '../../services/alert-service';
import { ScheduledPaymentService } from '../../services/scheduled-payment-service';

@Component({
  selector: 'app-schedule-payment-modal',
  imports: [CommonModule, FormsModule],
  templateUrl: './schedule-payment-modal.html',
  styleUrl: './schedule-payment-modal.scss'
})
export class SchedulePaymentModal implements OnInit {
   @ViewChild('schedulePaymentModal') dialogRef!: ElementRef<HTMLDialogElement>;

  selectedRecipientForSchedule: Recipient | null = null;

   newSchedule: Partial<ScheduledPayment> = {
      amount: 250,
      frequency: 'weekly',
      dayOfWeek: 1,
      time: '09:00',
      startDate: new Date(),
      isActive: true
    };

  constructor(private recipientService: RecipientService, private alertService: AlertService, private schedulePaymentService: ScheduledPaymentService) {}

  ngOnInit(): void {
    setInterval(() => this.schedulePaymentService.checkForDuePayments(), 1000);
  }

  open(recipient: Recipient) {
    this.selectedRecipientForSchedule = recipient;
    this.dialogRef.nativeElement.showModal();
    //this.resetNewSchedule();
  }

  addScheduledPayment() {
    if (!this.selectedRecipientForSchedule || !this.newSchedule.amount) return;

    // Check if we're editing an existing payment
    if (this.newSchedule.id) {
      this.updateScheduledPayment();
      return;
    }

    const payment: ScheduledPayment = {
      id: this.getNextPaymentId(),
      recipientId: this.selectedRecipientForSchedule.id,
      amount: this.newSchedule.amount,
      frequency: this.newSchedule.frequency as 'daily' | 'weekly' | 'monthly',
      dayOfWeek: this.newSchedule.dayOfWeek,
      dayOfMonth: this.newSchedule.dayOfMonth,
      time: this.newSchedule.time || '09:00',
      startDate: new Date(this.newSchedule.startDate || new Date()),
      endDate: this.newSchedule.endDate ? new Date(this.newSchedule.endDate) : undefined,
      isActive: true,
      nextExecution: this.calculateNextExecution(this.newSchedule),
      totalExecutions: 0
    };

    this.selectedRecipientForSchedule.scheduledPayments.push(payment);
    this.recipientService.recalculateRecipientTotals(this.selectedRecipientForSchedule);

    this.dialogRef.nativeElement.close();
    this.selectedRecipientForSchedule = null;

    this.alertService.show(`Payment schedule of ${payment.amount} ${payment.frequency} has been created`);
  }
    updateScheduledPayment() {
    if (!this.selectedRecipientForSchedule || !this.newSchedule.id) return;

    const paymentIndex = this.selectedRecipientForSchedule.scheduledPayments.findIndex(
      p => p.id === this.newSchedule.id
    );

    if (paymentIndex > -1) {
      const payment = this.selectedRecipientForSchedule.scheduledPayments[paymentIndex];
      
      // Update the payment with new values
      payment.amount = this.newSchedule.amount!;
      payment.frequency = this.newSchedule.frequency as 'daily' | 'weekly' | 'monthly';
      payment.dayOfWeek = this.newSchedule.dayOfWeek;
      payment.dayOfMonth = this.newSchedule.dayOfMonth;
      payment.time = this.newSchedule.time || '09:00';
      payment.startDate = new Date(this.newSchedule.startDate || new Date());
      payment.endDate = this.newSchedule.endDate ? new Date(this.newSchedule.endDate) : undefined;
      payment.nextExecution = this.calculateNextExecution(this.newSchedule);

      this.recipientService.recalculateRecipientTotals(this.selectedRecipientForSchedule);
      this.dialogRef.nativeElement.close();
      this.selectedRecipientForSchedule = null;

      this.alertService.show('Payment schedule has been updated successfully');
    }
  }
  private calculateNextExecution(schedule: Partial<ScheduledPayment>): Date {
  const now = new Date();
  const [hours, minutes] = (schedule.time || '09:00').split(':').map(Number);

  switch (schedule.frequency) {
    case 'daily':
      const todayAtTime = new Date(now);
      todayAtTime.setHours(hours, minutes, 0, 0);

      // If the target time today is still ahead, use it
      if (todayAtTime > now) {
        return todayAtTime;
      }

      // Otherwise, schedule for tomorrow
      const nextDay = new Date(now);
      nextDay.setDate(now.getDate() + 1);
      nextDay.setHours(hours, minutes, 0, 0);
      return nextDay;

    case 'weekly':
      return this.getNextWeekday(schedule.dayOfWeek || 1, schedule.time || '09:00');

    case 'monthly':
      const nextMonth = new Date(now);
      nextMonth.setMonth(now.getMonth() + 1);
      nextMonth.setDate(schedule.dayOfMonth || 1);
      nextMonth.setHours(hours, minutes, 0, 0);
      return nextMonth;

    default:
      return now;
  }
}
    private getNextPaymentId(): number {
    const allPayments = this.recipientService.getAllRecipients().flatMap(r => r.scheduledPayments);
    return Math.max(...allPayments.map(p => p.id), 0) + 1;
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

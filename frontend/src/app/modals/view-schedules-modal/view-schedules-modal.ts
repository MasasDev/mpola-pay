import { Component, ElementRef, ViewChild, OnInit } from '@angular/core';
import { Recipient } from '../../interfaces/recipient';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ScheduledPayment } from '../../interfaces/scheduled-payment';
import { RecipientService } from '../../services/recipient-service';
import { SchedulePaymentModal } from '../schedule-payment-modal/schedule-payment-modal';

@Component({
  selector: 'app-view-schedules-modal',
  standalone: true,
  imports: [CommonModule, FormsModule, SchedulePaymentModal],
  templateUrl: './view-schedules-modal.html',
  styleUrl: './view-schedules-modal.scss'
})
export class ViewSchedulesModal{
  @ViewChild('viewSchedulesModal') dialogRef!: ElementRef<HTMLDialogElement>;
  @ViewChild('scheduleModal') schedulePaymentModal!: SchedulePaymentModal;

  selectedRecipientForSchedule!: Recipient;
  depositAmount: number = 0;
  newSchedule!: ScheduledPayment;

  constructor(private recipientService: RecipientService) {}

  open(selectedRecipientForSchedule: Recipient) {
    this.selectedRecipientForSchedule = selectedRecipientForSchedule;
    this.dialogRef.nativeElement.showModal();
  }

  addScheduledPayment() {
    this.schedulePaymentModal.open(this.selectedRecipientForSchedule);
  }

  editScheduledPayment(payment: ScheduledPayment) {
    const recipient = this.recipientService.getAllRecipients().find(r => r.id === payment.recipientId);
    if (recipient) {
      this.selectedRecipientForSchedule = recipient;

      this.newSchedule = {
        id: payment.id,
        recipientId: payment.recipientId,
        amount: payment.amount,
        frequency: payment.frequency,
        dayOfWeek: payment.dayOfWeek,
        dayOfMonth: payment.dayOfMonth,
        time: payment.time,
        startDate: payment.startDate,
        endDate: payment.endDate,
        isActive: payment.isActive,
        nextExecution: payment.nextExecution,
        totalExecutions: payment.totalExecutions
      };

      this.dialogRef.nativeElement.close();
    }
  }

  toggleScheduleStatus(payment: ScheduledPayment) {
    payment.isActive = !payment.isActive;
    const action = payment.isActive ? 'resumed' : 'paused';

    const recipient = this.recipientService.getAllRecipients().find(r => r.id === payment.recipientId);
    if (recipient) {
      this.recipientService.recalculateRecipientTotals(recipient);
    }

    console.log(`Payment schedule ${action} successfully`);
  }

  deleteScheduledPayment(payment: ScheduledPayment) {
    const confirmMessage = `Are you sure you want to delete this scheduled payment of ${payment.amount} ${payment.frequency}?`;

    if (confirm(confirmMessage)) {
      const recipient = this.recipientService.getAllRecipients().find(r => r.id === payment.recipientId);
      if (recipient) {
        const paymentIndex = recipient.scheduledPayments.findIndex(p => p.id === payment.id);
        if (paymentIndex > -1) {
          recipient.scheduledPayments.splice(paymentIndex, 1);
          this.recipientService.recalculateRecipientTotals(recipient);
          console.log(`Scheduled payment of ${payment.amount} deleted successfully`);
        }
      }
    }
  }

  public getDayName(dayOfWeek?: number): string {
    if (dayOfWeek === undefined) return '';
    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[dayOfWeek] || '';
  }

  getTimeUntilPayment(date: Date): string {
    const now = new Date();
    const diffMs = date.getTime() - now.getTime();

    if (diffMs <= 0) return 'Now';

    const totalSeconds = Math.floor(diffMs / 1000);
    const days = Math.floor(totalSeconds / (60 * 60 * 24));
    const hours = Math.floor((totalSeconds % (60 * 60 * 24)) / (60 * 60));
    const minutes = Math.floor((totalSeconds % (60 * 60)) / 60);
    const seconds = totalSeconds % 60;

    if (days > 0) return `in ${days}d ${hours}h`;
    if (hours > 0) return `in ${hours}h ${minutes}m`;
    if (minutes > 0) return `in ${minutes}m ${seconds}s`;
    return `in ${seconds}s`;
  }
}

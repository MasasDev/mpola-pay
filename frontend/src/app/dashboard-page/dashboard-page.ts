import { Component, ViewChild, OnInit, signal, Signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Recipient } from '../interfaces/recipient';
import { ScheduledPayment } from '../interfaces/scheduled-payment';
import { ViewSchedulesModal } from '../modals/view-schedules-modal/view-schedules-modal';
import { AddRecipientModal } from '../modals/add-recipient-modal/add-recipient-modal';
import { SchedulePaymentModal } from '../modals/schedule-payment-modal/schedule-payment-modal';
import { DepositModal } from '../modals/deposit-modal/deposit-modal';
import { RecipientService } from '../services/recipient-service';
import { BalanceService } from '../services/balance-service';

@Component({
  selector: 'app-dashboard-page',
  imports: [FormsModule, CommonModule, DatePipe, ViewSchedulesModal, AddRecipientModal, SchedulePaymentModal, DepositModal],
  templateUrl: './dashboard-page.html',
  styleUrl: './dashboard-page.scss'
})
export class DashboardPage implements OnInit {
 
  @ViewChild(ViewSchedulesModal) viewSchedulesModal!: ViewSchedulesModal;
  @ViewChild(AddRecipientModal) addRecipientModal!: AddRecipientModal;
  @ViewChild(SchedulePaymentModal) schedulePaymentModal!: SchedulePaymentModal;
  @ViewChild(DepositModal) depositModal!: DepositModal;

  recipients: Recipient[] = [];
  
  searchTerm = '';
  selectedRecipients: number[] = [];

  constructor(private recipientService: RecipientService, public balanceService: BalanceService) {}

  ngOnInit(): void {
    this.refreshRecipients();
  }
  refreshRecipients() {
    this.recipients = this.recipientService.getAllRecipients();
  }

  // Modal methods
  openAddRecipientModal() {
    this.addRecipientModal.open();
  }

  openScheduleModal(recipient: Recipient) {
    this.schedulePaymentModal.open(recipient);
  }

  openDepositModal() {
    this.depositModal.open();
  }
  openBulkScheduleModal() {
    // Implementation for bulk scheduling
    console.log('Bulk schedule for recipients:', this.selectedRecipients);
  }


  deleteRecipient(id: number) {
    if (confirm('Are you sure you want to delete this recipient and all scheduled payments?')) {
      this.recipientService.deleteRecipient(id);
      this.refreshRecipients();
    }
  }

  editRecipient(recipient: Recipient) {
    console.log('Edit recipient:', recipient);
  }

  viewHistory(recipient: Recipient) {
    console.log('View history for:', recipient);
  }

  viewSchedules(recipient: Recipient) {
    this.viewSchedulesModal.open(recipient);
  }

  pauseSchedule(recipient: Recipient) {
    recipient.scheduledPayments.forEach(p => p.isActive = false);
    console.log('Paused schedules for:', recipient.name);
  }

  pauseSelected() {
    this.selectedRecipients.forEach(id => {
      const recipient = this.recipients.find(r => r.id === id);
      if (recipient) {
        recipient.scheduledPayments.forEach(p => p.isActive = false);
      }
    });
    this.selectedRecipients = [];
  }

  // Selection methods
  toggleSelection(id: number) {
    const index = this.selectedRecipients.indexOf(id);
    if (index > -1) {
      this.selectedRecipients.splice(index, 1);
    } else {
      this.selectedRecipients.push(id);
    }
  }

  selectAll() {
    if (this.selectedRecipients.length === this.recipients.length) {
      this.selectedRecipients = [];
    } else {
      this.selectedRecipients = this.recipients.map(r => r.id);
    }
  }

  // Utility methods
  getFilteredRecipients(): Recipient[] {
    if (!this.searchTerm) return this.recipients;
    return this.recipients.filter(r => 
      r.name.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
      r.email.toLowerCase().includes(this.searchTerm.toLowerCase())
    );
  }

  getTotalScheduled(): number {
    return this.recipients.reduce((sum, r) => sum + r.totalScheduled, 0);
  }

  getNextPaymentTime(): string {
    const upcomingPayments = this.getUpcomingPayments();
    if (upcomingPayments.length === 0) return 'None scheduled';
    
    const next = upcomingPayments[0];
    const now = new Date();
    const diff = next.nextExecution.getTime() - now.getTime();
    const days = Math.ceil(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    return `${days} days`;
  }

  getUpcomingPayments(): ScheduledPayment[] {
    const allPayments = this.recipients.flatMap(r => r.scheduledPayments.filter(p => p.isActive));
    return allPayments.sort((a, b) => a.nextExecution.getTime() - b.nextExecution.getTime());
  }

  getRecipientName(id: number): string {
    return this.recipients.find(r => r.id === id)?.name || 'Unknown';
  }

  getInitials(name: string): string {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  }

  getTimeUntilPayment(date: Date): string {
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) return `in ${days}d`;
    if (hours > 0) return `in ${hours}h`;
    return 'Soon';
  }

  getActivePaymentAmount(recipient: Recipient): number {
    return recipient.scheduledPayments
      .filter(p => p.isActive)
      .reduce((sum, p) => sum + p.amount, 0);
  }

  getPaymentFrequency(recipient: Recipient): string {
    const frequencies = recipient.scheduledPayments
      .filter(p => p.isActive)
      .map(p => p.frequency);
    return frequencies.length > 0 ? frequencies[0] : '';
  }

  getRecipientStatus(recipient: Recipient): string {
    if (recipient.status === 'inactive') return 'Inactive';
    if (this.hasActiveSchedule(recipient)) return 'Scheduled';
    return 'Active';
  }

  hasActiveSchedule(recipient: Recipient): boolean {
    return recipient.scheduledPayments.some(p => p.isActive);
  }

  getActiveScheduleCount(recipient: Recipient): number {
    return recipient.scheduledPayments.filter(p => p.isActive).length;
  }

  getPaymentProgress(recipient: Recipient): number {
    const activePayments = recipient.scheduledPayments.filter(p => p.isActive);
    if (activePayments.length === 0) return 0;
    
    const totalExecutions = activePayments.reduce((sum, p) => sum + p.totalExecutions, 0);
    const estimatedTotal = activePayments.length * 10; // Rough estimate
    return Math.min(Math.round((totalExecutions / estimatedTotal) * 100), 100);
  }

  
}
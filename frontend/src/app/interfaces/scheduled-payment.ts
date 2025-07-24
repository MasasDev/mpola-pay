export interface ScheduledPayment {
    id: number;
  recipientId: number;
  amount: number;
  frequency: 'daily' | 'weekly' | 'monthly';
  dayOfWeek?: number; // 0-6 for weekly
  dayOfMonth?: number; // 1-31 for monthly
  time: string; // HH:mm format
  startDate: Date;
  endDate?: Date;
  isActive: boolean;
  nextExecution: Date;
  totalExecutions: number;
  remainingAmount?: number;
}

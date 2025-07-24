import { ScheduledPayment } from "./scheduled-payment";

export interface Recipient {
    id: number;
  name: string;
  email: string;
  phone?: string;
  status: 'active' | 'inactive';
  scheduledPayments: ScheduledPayment[];
  totalScheduled: number;
  nextPayment?: Date;
  createdAt: Date;
}

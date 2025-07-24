import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class BalanceService {
  currentBalance = signal(2500);

  getCurrentBalance() {
    return this.currentBalance();
  }

  updateBalance(amount: number) {
    this.currentBalance.set(this.currentBalance() + amount);
  }
}

import { Component, ElementRef, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { BalanceService } from '../../services/balance-service';

@Component({
  selector: 'app-deposit-modal',
  imports: [CommonModule, FormsModule],
  templateUrl: './deposit-modal.html',
  styleUrl: './deposit-modal.scss'
})
export class DepositModal {
  @ViewChild('depositModal') dialogRef!: ElementRef<HTMLDialogElement>;
  depositAmount: number = 0;

  constructor(private balanceService: BalanceService) {}

  open() {
    this.dialogRef.nativeElement.showModal();
    this.depositAmount = 0;
  }

  depositFunds() {
    if (this.depositAmount > 0) {
      this.balanceService.updateBalance(this.depositAmount);
      this.dialogRef.nativeElement.close();
    }
  }
}

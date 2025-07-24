import { Component, Input, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AlertService, AlertModel, AlertType  } from '../../services/alert-service';
import { Console } from 'console';

@Component({
  selector: 'app-alert',
  imports: [CommonModule],
  templateUrl: './alert.html',
  styleUrl: './alert.scss'
})
export class Alert {

 constructor(public alertService: AlertService) {}

  get alert(): AlertModel | null {
    return this.alertService.alert();
    console.log(this.alert);
  }

  get alertClasses(): string {
    if (!this.alert) return '';

    return `alert alert-${this.alert.type}`;
  }

  get iconPath(): string {
    if (!this.alert) return '';

    switch (this.alert.type) {
      case 'success':
        return 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z';
      case 'error':
        return 'M6 18L18 6M6 6l12 12';
      case 'warning':
        return 'M12 8v4m0 4h.01M12 2a10 10 0 100 20 10 10 0 000-20z';
      case 'info':
        return 'M13 16h-1v-4h-1m1-4h.01M12 2a10 10 0 100 20 10 10 0 000-20z';
      default:
        return '';
    }
  }
}

import { Injectable, signal } from '@angular/core';

export type AlertType = 'success' | 'error' | 'warning' | 'info';

export interface AlertModel {
  message: string;
  type: AlertType;
}

@Injectable({ providedIn: 'root' })
export class AlertService {
  private _alert = signal<AlertModel | null>(null);
  public alert = this._alert.asReadonly();

  private timeoutId?: ReturnType<typeof setTimeout>;

  show(message: string, type: AlertType = 'info', durationMs = 5000) {
    // Clear previous timeout if any
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = undefined;
    }

    this._alert.set({ message, type });

    if (durationMs > 0) {
      this.timeoutId = setTimeout(() => {
        this.clear();
      }, durationMs);
    }
  }

  clear() {
    this._alert.set(null);
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = undefined;
    }
  }
}

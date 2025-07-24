import { Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { Recipient } from '../../interfaces/recipient';
import {CommonModule} from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RecipientService } from '../../services/recipient-service';
import { AlertService } from '../../services/alert-service';

@Component({
  selector: 'app-add-recipient-modal',
  imports: [CommonModule, FormsModule],
  templateUrl: './add-recipient-modal.html',
  styleUrl: './add-recipient-modal.scss'
})
export class AddRecipientModal {
  @ViewChild('addRecipientModal') dialogRef!: ElementRef<HTMLDialogElement>;
  @Output() onSuccess = new EventEmitter<void>();

  newRecipient: Partial<Recipient> = {
    name: '',
    email: '',
    phone: '',
    status: 'active'
  };

  constructor(private recipientService: RecipientService, private alertService: AlertService) {}

  open(){
    this.dialogRef.nativeElement.showModal();
  }
  addRecipient() {
    this.recipientService.addRecipient(this.newRecipient as Recipient);
    this.dialogRef.nativeElement.close();
    this.onSuccess.emit();
    this.newRecipient = { name: '', email: '', phone: '', status: 'active' };
    this.alertService.show('Recipient added successfully!', 'success', 3000);
  }

}

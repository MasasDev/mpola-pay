import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddRecipientModal } from './add-recipient-modal';

describe('AddRecipientModal', () => {
  let component: AddRecipientModal;
  let fixture: ComponentFixture<AddRecipientModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddRecipientModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddRecipientModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SchedulePaymentModal } from './schedule-payment-modal';

describe('SchedulePaymentModal', () => {
  let component: SchedulePaymentModal;
  let fixture: ComponentFixture<SchedulePaymentModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SchedulePaymentModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SchedulePaymentModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

import { TestBed } from '@angular/core/testing';

import { ScheduledPaymentService } from './scheduled-payment-service';

describe('ScheduledPaymentService', () => {
  let service: ScheduledPaymentService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ScheduledPaymentService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

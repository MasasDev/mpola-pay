import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DepositModal } from './deposit-modal';

describe('DepositModal', () => {
  let component: DepositModal;
  let fixture: ComponentFixture<DepositModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DepositModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DepositModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

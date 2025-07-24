import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewSchedulesModal } from './view-schedules-modal';

describe('ViewSchedulesModal', () => {
  let component: ViewSchedulesModal;
  let fixture: ComponentFixture<ViewSchedulesModal>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewSchedulesModal]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ViewSchedulesModal);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

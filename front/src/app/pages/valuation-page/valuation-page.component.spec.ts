import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ValuationPageComponent } from './valuation-page.component';

describe('ValuationPageComponent', () => {
  let component: ValuationPageComponent;
  let fixture: ComponentFixture<ValuationPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ValuationPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ValuationPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

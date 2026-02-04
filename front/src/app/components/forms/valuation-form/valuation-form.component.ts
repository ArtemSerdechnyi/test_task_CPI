import {
  Component,
  DestroyRef,
  EventEmitter,
  inject,
  Input,
  Output,
} from '@angular/core';
import { FormBuilder, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import {
  PropertyType,
  ValuationCalculateRequest,
} from '../../../models/valuation.models';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-valuation-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './valuation-form.component.html',
  styleUrl: './valuation-form.component.scss',
})
export class ValuationFormComponent {
  private readonly fb = inject(FormBuilder);
  private readonly destroyRef = inject(DestroyRef);
  @Output() calculate = new EventEmitter<ValuationCalculateRequest>();
  @Input() submitting = false;

  readonly propertyTypes: Array<{ label: string; value: PropertyType }> = [
    { label: 'Residential (Wohnen)', value: 'residential' },
    { label: 'Commercial (Gewerbe)', value: 'commercial' },
  ];

  readonly form = this.createForm();

  constructor() {
    this.handlePropertyTypeChanges();
  }

  private createForm() {
    return this.fb.nonNullable.group({
      propertyType: ['residential' as PropertyType, Validators.required],
      purchaseDate: ['', Validators.required],
      monthlyNetColdRentEur: [0, [Validators.required, Validators.min(0.01)]],
      areaSqm: [0, [Validators.required, Validators.min(0.01)]],
      numberOfResidentialUnits: [1, [Validators.required, Validators.min(1)]],
      numberOfParkingUnits: [0, [Validators.required, Validators.min(0)]],
      standardLandValueEurPerSqm: [
        0,
        [Validators.required, Validators.min(0.01)],
      ],
      plotAreaSqm: [0, [Validators.required, Validators.min(0.01)]],
      remainingUsefulLifeYears: [
        0,
        [Validators.required, Validators.min(0.01)],
      ],
      propertyYieldPercent: [
        0,
        [Validators.required, Validators.min(0.01), Validators.max(100)],
      ],
      actualPurchasePriceEur: [0, [Validators.required, Validators.min(0.01)]],
    });
  }

  private handlePropertyTypeChanges(): void {
    this.form.controls.propertyType.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((type) => {
        const ctrl = this.form.controls.numberOfResidentialUnits;

        if (type === 'residential') {
          ctrl.enable({ emitEvent: false });
          ctrl.setValidators([Validators.required, Validators.min(1)]);
          if (ctrl.value < 1) {
            ctrl.setValue(1, { emitEvent: false });
          }
        } else {
          ctrl.setValue(1, { emitEvent: false });
          ctrl.disable({ emitEvent: false });
          ctrl.clearValidators();
        }
        ctrl.updateValueAndValidity({ emitEvent: false });
      });
  }

  submit(): void {
    if (this.submitting) return;
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    const raw = this.form.getRawValue();

    const dto: ValuationCalculateRequest = {
      property_type:
        raw.propertyType === 'residential' ? 'residential' : 'commercial',
      purchase_date: raw.purchaseDate,

      monthly_net_rent: raw.monthlyNetColdRentEur,
      living_area: raw.areaSqm,

      parking_units: raw.numberOfParkingUnits,

      land_value_per_sqm: raw.standardLandValueEurPerSqm,
      plot_area: raw.plotAreaSqm,

      remaining_useful_life: raw.remainingUsefulLifeYears,
      property_yield: raw.propertyYieldPercent,

      actual_purchase_price: raw.actualPurchasePriceEur,

      ...(raw.propertyType === 'residential'
        ? { residential_units: raw.numberOfResidentialUnits }
        : {}),
    };

    this.calculate.emit(dto);
  }
}

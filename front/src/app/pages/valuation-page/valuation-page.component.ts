import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { finalize } from 'rxjs';

import { ValuationFormComponent } from '../../components/forms/valuation-form/valuation-form.component';
import { ValuationApiService } from '../../services/valuation-api.service';
import {
  ValuationCalculateRequest,
  ValuationResponseDto,
} from '../../models/valuation.models';

@Component({
  selector: 'app-valuation-page',
  standalone: true,
  imports: [CommonModule, ValuationFormComponent],
  templateUrl: './valuation-page.component.html',
  styleUrl: './valuation-page.component.scss',
})
export class ValuationPageComponent {
  private readonly valuationService = inject(ValuationApiService);

  isSubmitting = false;
  result: ValuationResponseDto | null = null;
  errorText: string | null = null;

  isAnalyzing = false;
  insightText: string | null = null;
  insightError: string | null = null;

  onCalculate(dto: ValuationCalculateRequest): void {
    this.isSubmitting = true;
    this.result = null;
    this.errorText = null;

    this.isAnalyzing = false;
    this.insightText = null;
    this.insightError = null;

    this.valuationService
      .calculate(dto)
      .pipe(finalize(() => (this.isSubmitting = false)))
      .subscribe({
        next: (res) => {
          this.result = res;
        },
        error: (err: unknown) => {
          this.errorText =
            err instanceof Error
              ? err.message
              : 'Request failed. Please try again.';
        },
      });
  }

  onGenerateInsight(): void {
    if (!this.result || this.isAnalyzing) return;

    this.isAnalyzing = true;
    this.insightText = null;
    this.insightError = null;

    this.valuationService
      .getAiAnalysis(this.result)
      .pipe(finalize(() => (this.isAnalyzing = false)))
      .subscribe({
        next: (text) => {
          this.insightText = this.normalizeInsight(text);
        },
        error: (err: unknown) => {
          this.insightError =
            err instanceof Error
              ? err.message
              : 'Analysis request failed. Please try again.';
        },
      });
  }

  private normalizeInsight(text: string): string {
    let s = String(text ?? '');

    const t = s.trim();
    if (
      (t.startsWith('"') && t.endsWith('"')) ||
      (t.startsWith("'") && t.endsWith("'"))
    ) {
      try {
        s = JSON.parse(t);
      } catch {
        s = t.slice(1, -1);
      }
    }

    s = s.replace(/\\n/g, '\n');

    return s.trim();
  }
}

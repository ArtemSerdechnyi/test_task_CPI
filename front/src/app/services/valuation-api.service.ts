import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import {
  InsightResponseDto,
  ValuationCalculateRequest,
  ValuationResponseDto,
} from '../models/valuation.models';

@Injectable({ providedIn: 'root' })
export class ValuationApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://localhost:8000';

  calculate(dto: ValuationCalculateRequest): Observable<ValuationResponseDto> {
    return this.http
      .post<ValuationResponseDto>(
        `${this.baseUrl}/api/valuation/calculate`,
        dto,
      )
      .pipe(
        catchError((error: HttpErrorResponse) => {
          let message = 'Request failed. Please try again.';

          if (error.status === 0) {
            message = 'Cannot reach server. Please check your connection.';
          } else if (error.status >= 400 && error.status < 500) {
            message =
              error.error?.message ||
              'Invalid request. Please check your input.';
          } else if (error.status >= 500) {
            message =
              error.error?.message ||
              'Server error occurred. Please try again later.';
          }

          return throwError(() => new Error(message));
        }),
      );
  }

  getAiAnalysis(dto: ValuationResponseDto): Observable<string> {
    return this.http
      .post(`${this.baseUrl}/api/valuation/calculate/analysis`, dto, {
        responseType: 'text',
      })
      .pipe(
        catchError((error: HttpErrorResponse) => {
          let message = 'Analysis request failed. Please try again.';

          if (error.status === 0) {
            message = 'Cannot reach server. Please check your connection.';
          } else if (error.status >= 400 && error.status < 500) {
            message =
              (typeof error.error === 'string' && error.error) ||
              error.error?.message ||
              'Invalid request. Please check your input.';
          } else if (error.status >= 500) {
            message =
              (typeof error.error === 'string' && error.error) ||
              error.error?.message ||
              'Server error occurred. Please try again later.';
          }

          return throwError(() => new Error(message));
        }),
      );
  }
}

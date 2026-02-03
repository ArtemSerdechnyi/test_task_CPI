import { Routes } from '@angular/router';
import { ValuationPageComponent } from './pages/valuation-page/valuation-page.component';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'valuation' },
  { path: 'valuation', component: ValuationPageComponent },
  { path: '**', redirectTo: 'valuation' },
];

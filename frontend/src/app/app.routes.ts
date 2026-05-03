import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'preferences',
    loadComponent: () =>
      import('./preferences/preferences.component').then((m) => m.PreferencesComponent)
  },
  {
    path: 'intelligence',
    loadComponent: () =>
      import('./intelligence/intelligence.component').then((m) => m.IntelligenceComponent)
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: ''
  }
];

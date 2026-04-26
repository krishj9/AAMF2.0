import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'preferences',
    loadComponent: () =>
      import('./preferences/preferences.component').then((m) => m.PreferencesComponent)
  },
  {
    path: '',
    pathMatch: 'full',
    redirectTo: ''
  }
];

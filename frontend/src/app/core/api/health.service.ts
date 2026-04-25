import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { apiUrl } from './api-config';

export interface HealthResponse {
  status: string;
  app: string;
  environment: string;
  schema_version: string;
  policy_version: string;
}

@Injectable({ providedIn: 'root' })
export class HealthService {
  private readonly http = inject(HttpClient);

  getHealth() {
    return this.http.get<HealthResponse>(apiUrl('/health'));
  }
}

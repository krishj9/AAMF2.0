import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';

import { PortfolioRecord } from './rebalance.models';

@Injectable({ providedIn: 'root' })
export class PortfolioService {
  private readonly http = inject(HttpClient);

  list() {
    return this.http.get<PortfolioRecord[]>('/api/portfolios');
  }
}

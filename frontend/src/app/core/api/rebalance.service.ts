import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import { OrchestrationResponse, PortfolioRebalanceRequest } from './rebalance.models';

@Injectable({ providedIn: 'root' })
export class RebalanceService {
  private readonly http = inject(HttpClient);

  submit(request: PortfolioRebalanceRequest) {
    return this.http.post<OrchestrationResponse>('/api/rebalance', request);
  }
}

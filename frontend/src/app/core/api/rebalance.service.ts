import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';

import {
  ApprovalTransitionResult,
  OrchestrationResponse,
  PortfolioRebalanceRequest
} from './rebalance.models';

@Injectable({ providedIn: 'root' })
export class RebalanceService {
  private readonly http = inject(HttpClient);

  submit(request: PortfolioRebalanceRequest) {
    return this.http.post<OrchestrationResponse>('/api/rebalance', request);
  }

  approve(approvalId: string, recommendationHash: string) {
    return this.http.post<ApprovalTransitionResult>(`/api/approvals/${approvalId}/actions`, {
      action: 'APPROVE',
      actor_id: 'local_owner',
      expected_recommendation_hash: recommendationHash
    });
  }

  reject(approvalId: string, recommendationHash: string, note: string) {
    return this.http.post<ApprovalTransitionResult>(`/api/approvals/${approvalId}/actions`, {
      action: 'REJECT',
      actor_id: 'local_owner',
      note,
      expected_recommendation_hash: recommendationHash
    });
  }
}

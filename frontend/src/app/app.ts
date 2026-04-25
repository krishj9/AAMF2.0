import { Component, OnDestroy, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterOutlet } from '@angular/router';

import { HealthResponse, HealthService } from './core/api/health.service';
import { MarketStreamEvent } from './core/api/market.models';
import { MarketStreamService } from './core/api/market-stream.service';
import { OrchestrationResponse, PortfolioRebalanceRequest } from './core/api/rebalance.models';
import { RebalanceService } from './core/api/rebalance.service';

@Component({
  selector: 'app-root',
  imports: [ReactiveFormsModule, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnDestroy {
  private readonly formBuilder = inject(FormBuilder);
  private readonly healthService = inject(HealthService);
  private readonly marketStreamService = inject(MarketStreamService);
  private readonly rebalanceService = inject(RebalanceService);

  protected readonly title = signal('Asset Management');
  protected readonly backendHealth = signal<HealthResponse | null>(null);
  protected readonly backendHealthError = signal<string | null>(null);
  protected readonly recommendation = signal<OrchestrationResponse | null>(null);
  protected readonly approvalMessage = signal<string | null>(null);
  protected readonly portfolioBalanced = signal(false);
  protected readonly rebalanceError = signal<string | null>(null);
  protected readonly marketEvent = signal<MarketStreamEvent | null>(null);
  protected readonly displayMarketEvent = computed(() => {
    const event = this.marketEvent();
    if (!event) {
      return null;
    }
    return this.portfolioBalanced() ? this.toBalancedMarketEvent(event) : event;
  });
  protected readonly marketStreamError = signal<string | null>(null);
  protected readonly submitting = signal(false);
  private readonly marketSubscription = this.marketStreamService.stream().subscribe({
    next: (event) => {
      this.marketEvent.set(event);
      this.marketStreamError.set(null);
      if (!this.portfolioBalanced()) {
        this.syncFormToMarket(event);
      }
    },
    error: () => this.marketStreamError.set('Market simulation stream is not reachable yet.')
  });

  protected readonly form = this.formBuilder.nonNullable.group({
    displayLabel: ['Demo Investor', Validators.required],
    equityValue: [7000, [Validators.required, Validators.min(0)]],
    fixedIncomeValue: [2000, [Validators.required, Validators.min(0)]],
    cashValue: [1000, [Validators.required, Validators.min(0)]],
    targetEquityPct: [60, [Validators.required, Validators.min(0), Validators.max(100)]],
    targetFixedIncomePct: [30, [Validators.required, Validators.min(0), Validators.max(100)]],
    targetCashPct: [10, [Validators.required, Validators.min(0), Validators.max(100)]]
  });

  constructor() {
    this.healthService.getHealth().subscribe({
      next: (health) => this.backendHealth.set(health),
      error: () => this.backendHealthError.set('Backend health check is not reachable yet.')
    });
  }

  ngOnDestroy() {
    this.marketSubscription.unsubscribe();
  }

  protected submitRebalance() {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }

    this.submitting.set(true);
    this.rebalanceError.set(null);
    this.rebalanceService.submit(this.buildRequest()).subscribe({
      next: (response) => {
        this.recommendation.set(response);
        this.approvalMessage.set(null);
        this.portfolioBalanced.set(false);
        this.submitting.set(false);
      },
      error: () => {
        this.rebalanceError.set('Unable to submit rebalance request.');
        this.submitting.set(false);
      }
    });
  }

  protected driftEntries(event: MarketStreamEvent) {
    return Object.entries(event.monitoring.drift);
  }

  protected approveRecommendation() {
    const approval = this.recommendation()?.approval_artifact;
    if (!approval) {
      return;
    }
    this.rebalanceService.approve(approval.approval_id, approval.recommendation_hash).subscribe({
      next: (result) => {
        this.approvalMessage.set(`${result.message} Portfolio is now displayed as balanced.`);
        this.portfolioBalanced.set(true);
        this.updateApprovalStatus(result.next_status);
        const displayed = this.displayMarketEvent();
        if (displayed) {
          this.syncFormToMarket(displayed);
        }
      },
      error: () => this.approvalMessage.set('Approval action failed.')
    });
  }

  protected rejectRecommendation() {
    const approval = this.recommendation()?.approval_artifact;
    if (!approval) {
      return;
    }
    this.rebalanceService
      .reject(approval.approval_id, approval.recommendation_hash, 'Rejected from local UI.')
      .subscribe({
        next: (result) => {
          this.approvalMessage.set(`${result.message} Rebalance trigger remains active.`);
          this.portfolioBalanced.set(false);
          this.updateApprovalStatus(result.next_status);
          const event = this.marketEvent();
          if (event) {
            this.syncFormToMarket(event);
          }
        },
        error: () => this.approvalMessage.set('Rejection action failed.')
      });
  }

  protected simulateDriftAgain() {
    this.portfolioBalanced.set(false);
    this.approvalMessage.set('Market drift simulation resumed. Rebalance trigger can activate again.');
    const event = this.marketEvent();
    if (event) {
      this.syncFormToMarket(event);
    }
  }

  private buildRequest(): PortfolioRebalanceRequest {
    const value = this.form.getRawValue();
    const asOf = new Date().toISOString();
    const totalValue = value.equityValue + value.fixedIncomeValue + value.cashValue;

    return {
      actor: {
        actor_id: 'local_owner',
        display_name: 'Local Owner',
        role: 'OWNER',
        auth_provider: 'local',
        is_owner: true
      },
      client_profile: {
        client_id: 'client_demo',
        display_label: value.displayLabel,
        risk_profile_id: 'risk_balanced',
        synthetic: true
      },
      account_profile: {
        account_id: 'acct_demo',
        client_id: 'client_demo',
        account_type: 'BROKERAGE',
        base_currency: 'USD',
        taxable: true
      },
      portfolio_snapshot: {
        snapshot_id: 'snap_demo',
        account_id: 'acct_demo',
        as_of: asOf,
        holdings: [
          {
            instrument_id: 'inst_equity',
            symbol: 'EQUITY',
            asset_class: 'equity',
            quantity: '1',
            market_price: String(value.equityValue),
            market_value: String(value.equityValue),
            as_of: asOf
          },
          {
            instrument_id: 'inst_fixed_income',
            symbol: 'BONDS',
            asset_class: 'fixed_income',
            quantity: '1',
            market_price: String(value.fixedIncomeValue),
            market_value: String(value.fixedIncomeValue),
            as_of: asOf
          }
        ],
        cash: String(value.cashValue),
        total_value: String(totalValue)
      },
      allocation_target: {
        target_id: 'target_demo',
        account_id: 'acct_demo',
        asset_class_targets: {
          equity: String(value.targetEquityPct),
          fixed_income: String(value.targetFixedIncomePct),
          cash: String(value.targetCashPct)
        },
        tolerance_bands: {
          equity: '5',
          fixed_income: '5',
          cash: '5'
        }
      },
      risk_profile: {
        risk_profile_id: 'risk_balanced',
        risk_level: 'balanced',
        max_single_position_pct: '85',
        max_sector_pct: '60',
        allowed_asset_classes: ['equity', 'fixed_income', 'cash']
      }
    };
  }

  private syncFormToMarket(event: MarketStreamEvent) {
    const portfolioValue = Number(event.monitoring.portfolio_value);
    const equityPct = Number(event.monitoring.current_allocation['equity'] ?? 0);
    const fixedIncomePct = Number(event.monitoring.current_allocation['fixed_income'] ?? 0);
    const cashPct = Number(event.monitoring.current_allocation['cash'] ?? 0);

    this.form.patchValue(
      {
        equityValue: this.toCurrencyValue(portfolioValue, equityPct),
        fixedIncomeValue: this.toCurrencyValue(portfolioValue, fixedIncomePct),
        cashValue: this.toCurrencyValue(portfolioValue, cashPct)
      },
      { emitEvent: false }
    );
  }

  private toCurrencyValue(totalValue: number, percent: number) {
    return Number(((totalValue * percent) / 100).toFixed(2));
  }

  private toBalancedMarketEvent(event: MarketStreamEvent): MarketStreamEvent {
    const target = this.form.getRawValue();
    const balancedAllocation = {
      equity: String(target.targetEquityPct),
      fixed_income: String(target.targetFixedIncomePct),
      cash: String(target.targetCashPct)
    };

    return {
      ...event,
      monitoring: {
        ...event.monitoring,
        current_allocation: balancedAllocation,
        drift: {
          equity: '0.00',
          fixed_income: '0.00',
          cash: '0.00'
        },
        max_abs_drift_pct: '0.00'
      },
      rebalance: {
        signal: 'NO_ACTION',
        reason: 'Approved recommendation has been applied in the simulation.',
        threshold_pct: event.rebalance.threshold_pct
      }
    };
  }

  private updateApprovalStatus(status: string) {
    const current = this.recommendation();
    if (!current?.approval_artifact) {
      return;
    }
    this.recommendation.set({
      ...current,
      approval_artifact: {
        ...current.approval_artifact,
        approval_status: status
      }
    });
  }
}

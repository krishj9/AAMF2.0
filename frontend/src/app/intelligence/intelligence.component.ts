import { TitleCasePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';

import { apiUrl } from '../core/api/api-config';
import { PortfolioService } from '../core/api/portfolio.service';
import { PortfolioRecord } from '../core/api/rebalance.models';

@Component({
  selector: 'app-intelligence',
  imports: [TitleCasePipe],
  templateUrl: './intelligence.component.html',
  styleUrl: './intelligence.component.scss',
})
export class IntelligenceComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly router = inject(Router);
  private readonly portfolioService = inject(PortfolioService);

  protected readonly portfolios = signal<PortfolioRecord[]>([]);
  protected readonly selectedAccountId = signal<string>('acct_demo');
  protected readonly selectedClientId = signal<string>('client_demo');

  protected readonly selectedPortfolio = computed(() =>
    this.portfolios().find(
      (p) => p.account_profile.account_id === this.selectedAccountId()
    ) ?? null
  );

  protected readonly activeTab = signal<'workflow' | 'memory' | 'audit'>('workflow');

  // Workflow trace
  protected readonly workflowTrace = signal<any>(null);
  protected readonly workflowLoading = signal(false);
  protected readonly workflowError = signal<string | null>(null);

  // Memory
  protected readonly memoryData = signal<any>(null);
  protected readonly memoryLoading = signal(false);
  protected readonly memoryError = signal<string | null>(null);

  // Audit
  protected readonly auditData = signal<any>(null);
  protected readonly auditLoading = signal(false);
  protected readonly auditError = signal<string | null>(null);

  ngOnInit() {
    this.portfolioService.list().subscribe({
      next: (portfolios) => {
        this.portfolios.set(portfolios);
        if (portfolios.length) {
          this.selectedAccountId.set(portfolios[0].account_profile.account_id);
          this.selectedClientId.set(portfolios[0].client_profile.client_id);
          this.loadAll();
        }
      },
    });
  }

  protected selectPortfolio(event: Event) {
    const accountId = (event.target as HTMLSelectElement).value;
    const portfolio = this.portfolios().find(
      (p) => p.account_profile.account_id === accountId
    );
    if (!portfolio) return;
    this.selectedAccountId.set(accountId);
    this.selectedClientId.set(portfolio.client_profile.client_id);
    this.loadAll();
  }

  protected setTab(tab: 'workflow' | 'memory' | 'audit') {
    this.activeTab.set(tab);
  }

  protected goBack() {
    this.router.navigate(['/']);
  }

  private loadAll() {
    this.loadWorkflowTrace();
    this.loadMemory();
    this.loadAudit();
  }

  protected loadWorkflowTrace() {
    this.workflowLoading.set(true);
    this.workflowError.set(null);
    this.http
      .get<any>(apiUrl(`/intelligence/workflow-trace/${this.selectedAccountId()}`))
      .subscribe({
        next: (data) => {
          this.workflowTrace.set(data);
          this.workflowLoading.set(false);
        },
        error: () => {
          this.workflowError.set('No workflow trace available yet. Run a rebalance first.');
          this.workflowLoading.set(false);
        },
      });
  }

  protected loadMemory() {
    this.memoryLoading.set(true);
    this.memoryError.set(null);
    this.http
      .get<any>(apiUrl(`/intelligence/memory/${this.selectedClientId()}`))
      .subscribe({
        next: (data) => {
          this.memoryData.set(data);
          this.memoryLoading.set(false);
        },
        error: () => {
          this.memoryError.set('Could not load memory data.');
          this.memoryLoading.set(false);
        },
      });
  }

  protected loadAudit() {
    this.auditLoading.set(true);
    this.auditError.set(null);
    this.http
      .get<any>(apiUrl(`/intelligence/audit/${this.selectedAccountId()}`))
      .subscribe({
        next: (data) => {
          this.auditData.set(data);
          this.auditLoading.set(false);
        },
        error: () => {
          this.auditError.set('Could not load audit trail.');
          this.auditLoading.set(false);
        },
      });
  }

  protected statusClass(status: string): string {
    const s = status?.toLowerCase() ?? '';
    if (s.includes('complet') || s.includes('success') || s === 'approved') return 'status--done';
    if (s.includes('block') || s.includes('fail') || s === 'rejected') return 'status--blocked';
    if (s.includes('process') || s.includes('running')) return 'status--running';
    return 'status--pending';
  }

  protected verdictClass(verdict: string): string {
    if (verdict === 'COMPLIANT') return 'badge--success';
    if (verdict === 'NON_COMPLIANT') return 'badge--danger';
    return 'badge--warning';
  }

  protected approvalClass(status: string): string {
    if (status === 'APPROVED') return 'badge--success';
    if (status === 'REJECTED') return 'badge--danger';
    return 'badge--muted';
  }

  protected formatDate(iso: string): string {
    if (!iso) return '—';
    return new Date(iso).toLocaleString();
  }

  protected objectEntries(obj: Record<string, string>): [string, string][] {
    return obj ? Object.entries(obj) : [];
  }
}

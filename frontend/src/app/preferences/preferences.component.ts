import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';

import { PreferenceProfile, PreferenceUpdateRequest } from '../core/api/preference.models';
import { PreferenceService } from '../core/api/preference.service';

@Component({
  selector: 'app-preferences',
  imports: [ReactiveFormsModule],
  templateUrl: './preferences.component.html',
  styleUrl: './preferences.component.scss'
})
export class PreferencesComponent implements OnInit {
  private readonly formBuilder = inject(FormBuilder);
  private readonly preferenceService = inject(PreferenceService);
  private readonly router = inject(Router);

  protected readonly currentStep = signal<'risk' | 'allocation' | 'constraints' | 'review'>('risk');
  protected readonly loading = signal(false);
  protected readonly saving = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly currentPreferences = signal<PreferenceProfile | null>(null);
  protected readonly clientId = signal('client_demo'); // TODO: Get from auth/route

  protected readonly riskForm = this.formBuilder.nonNullable.group({
    riskLevel: ['balanced', Validators.required],
    maxSinglePositionPct: [85, [Validators.required, Validators.min(1), Validators.max(100)]],
    maxSectorPct: [60, [Validators.required, Validators.min(1), Validators.max(100)]],
    allowedAssetClasses: [['equity', 'fixed_income', 'cash'], Validators.required]
  });

  protected readonly allocationForm = this.formBuilder.nonNullable.group({
    equityTarget: [60, [Validators.required, Validators.min(0), Validators.max(100)]],
    fixedIncomeTarget: [30, [Validators.required, Validators.min(0), Validators.max(100)]],
    cashTarget: [10, [Validators.required, Validators.min(0), Validators.max(100)]],
    equityTolerance: [5, [Validators.required, Validators.min(0), Validators.max(20)]],
    fixedIncomeTolerance: [5, [Validators.required, Validators.min(0), Validators.max(20)]],
    cashTolerance: [5, [Validators.required, Validators.min(0), Validators.max(20)]]
  });

  protected readonly constraintsForm = this.formBuilder.nonNullable.group({
    taxStrategy: ['none', Validators.required],
    esgPreference: ['none', Validators.required],
    dividendPreference: ['no_preference', Validators.required],
    excludedSectors: [[]]
  });

  protected readonly allocationTotal = computed(() => {
    const values = this.allocationForm.getRawValue();
    return values.equityTarget + values.fixedIncomeTarget + values.cashTarget;
  });

  protected readonly allocationValid = computed(() => {
    const total = this.allocationTotal();
    return Math.abs(total - 100) < 0.01;
  });

  protected readonly concentrationWarning = computed(() => {
    const riskValues = this.riskForm.getRawValue();
    const allocationValues = this.allocationForm.getRawValue();
    const maxConcentration = riskValues.maxSinglePositionPct;
    
    const warnings: string[] = [];
    
    if (allocationValues.equityTarget > maxConcentration) {
      warnings.push(`Equity target (${allocationValues.equityTarget}%) exceeds max concentration limit (${maxConcentration}%)`);
    }
    if (allocationValues.fixedIncomeTarget > maxConcentration) {
      warnings.push(`Fixed Income target (${allocationValues.fixedIncomeTarget}%) exceeds max concentration limit (${maxConcentration}%)`);
    }
    if (allocationValues.cashTarget > maxConcentration) {
      warnings.push(`Cash target (${allocationValues.cashTarget}%) exceeds max concentration limit (${maxConcentration}%)`);
    }
    
    return warnings;
  });

  protected readonly cashWarning = computed(() => {
    const allocationValues = this.allocationForm.getRawValue();
    if (allocationValues.cashTarget === 0) {
      return 'Warning: 0% cash allocation provides no liquidity buffer for rebalancing operations. Consider maintaining at least 5% cash.';
    }
    return null;
  });

  protected readonly hasValidationErrors = computed(() => {
    return !this.allocationValid() || this.concentrationWarning().length > 0;
  });

  protected readonly riskLevelOptions = [
    { value: 'conservative', label: 'Conservative', description: 'Minimize risk, focus on capital preservation' },
    { value: 'balanced', label: 'Balanced', description: 'Balance growth and stability' },
    { value: 'growth', label: 'Growth', description: 'Focus on growth with moderate risk' },
    { value: 'aggressive', label: 'Aggressive', description: 'Maximize growth potential' }
  ];

  protected readonly allocationPresets = [
    { name: 'Conservative', equity: 30, fixedIncome: 60, cash: 10 },
    { name: 'Moderate', equity: 50, fixedIncome: 40, cash: 10 },
    { name: 'Balanced', equity: 60, fixedIncome: 30, cash: 10 },
    { name: 'Growth', equity: 75, fixedIncome: 20, cash: 5 },
    { name: 'Aggressive', equity: 85, fixedIncome: 10, cash: 5 }
  ];

  // Map risk levels to allocation presets
  private readonly riskLevelToAllocation: Record<string, { equity: number; fixedIncome: number; cash: number }> = {
    'conservative': { equity: 30, fixedIncome: 60, cash: 10 },
    'balanced': { equity: 60, fixedIncome: 30, cash: 10 },
    'growth': { equity: 75, fixedIncome: 20, cash: 5 },
    'aggressive': { equity: 85, fixedIncome: 10, cash: 5 }
  };

  protected readonly taxStrategyOptions = [
    { value: 'none', label: 'No Special Strategy' },
    { value: 'tax_loss_harvesting', label: 'Tax-Loss Harvesting' },
    { value: 'minimize_short_term', label: 'Minimize Short-Term Gains' }
  ];

  protected readonly esgOptions = [
    { value: 'none', label: 'No ESG Requirements' },
    { value: 'esg_focused', label: 'ESG-Focused Investments' },
    { value: 'exclude_sectors', label: 'Exclude Specific Sectors' }
  ];

  protected readonly dividendOptions = [
    { value: 'no_preference', label: 'No Preference' },
    { value: 'prefer_dividends', label: 'Prefer Dividend-Paying Stocks' },
    { value: 'avoid_dividends', label: 'Avoid Dividends' }
  ];

  ngOnInit() {
    this.loadPreferences();
  }

  protected loadPreferences() {
    this.loading.set(true);
    this.error.set(null);

    this.preferenceService.getPreferences(this.clientId()).subscribe({
      next: (preferences) => {
        this.currentPreferences.set(preferences);
        this.populateFormsFromPreferences(preferences);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Failed to load preferences');
        this.loading.set(false);
      }
    });
  }

  protected populateFormsFromPreferences(preferences: PreferenceProfile) {
    // Populate risk form
    if (preferences.risk_profile) {
      this.riskForm.patchValue({
        riskLevel: preferences.risk_profile.risk_level,
        maxSinglePositionPct: Number(preferences.risk_profile.max_single_position_pct),
        maxSectorPct: Number(preferences.risk_profile.max_sector_pct),
        allowedAssetClasses: preferences.risk_profile.allowed_asset_classes
      });
    }

    // Populate allocation form
    const targets = preferences.allocation_target.asset_class_targets;
    const tolerances = preferences.allocation_target.tolerance_bands;
    this.allocationForm.patchValue({
      equityTarget: Number(targets['equity'] || 60),
      fixedIncomeTarget: Number(targets['fixed_income'] || 30),
      cashTarget: Number(targets['cash'] || 10),
      equityTolerance: Number(tolerances['equity'] || 5),
      fixedIncomeTolerance: Number(tolerances['fixed_income'] || 5),
      cashTolerance: Number(tolerances['cash'] || 5)
    });

    // Populate constraints form
    this.constraintsForm.patchValue({
      taxStrategy: preferences.constraints['tax_strategy'] || 'none',
      esgPreference: preferences.constraints['esg_preference'] || 'none',
      dividendPreference: preferences.constraints['dividend_preference'] || 'no_preference',
      excludedSectors: preferences.constraints['excluded_sectors'] || []
    });
  }

  protected nextStep() {
    const current = this.currentStep();
    
    if (current === 'risk') {
      if (this.riskForm.invalid) {
        this.riskForm.markAllAsTouched();
        console.error('Risk form is invalid:', this.riskForm.errors, this.riskForm.value);
        return;
      }
      console.log('Moving to allocation step. Risk form value:', this.riskForm.value);
      
      // Auto-populate allocation based on selected risk level
      const riskLevel = this.riskForm.value.riskLevel;
      if (riskLevel && this.riskLevelToAllocation[riskLevel]) {
        const allocation = this.riskLevelToAllocation[riskLevel];
        this.allocationForm.patchValue({
          equityTarget: allocation.equity,
          fixedIncomeTarget: allocation.fixedIncome,
          cashTarget: allocation.cash
        });
        console.log('Auto-populated allocation for risk level', riskLevel, ':', allocation);
      }
      
      this.currentStep.set('allocation');
    } else if (current === 'allocation') {
      if (this.allocationForm.invalid) {
        this.allocationForm.markAllAsTouched();
        console.error('Allocation form is invalid:', this.allocationForm.errors, this.allocationForm.value);
        return;
      }
      
      // Check for validation errors
      if (this.hasValidationErrors()) {
        this.allocationForm.markAllAsTouched();
        console.error('Allocation has validation errors:', {
          allocationValid: this.allocationValid(),
          concentrationWarnings: this.concentrationWarning()
        });
        return;
      }
      
      console.log('Moving to constraints step. Allocation form value:', this.allocationForm.value);
      this.currentStep.set('constraints');
    } else if (current === 'constraints') {
      if (this.constraintsForm.invalid) {
        this.constraintsForm.markAllAsTouched();
        console.error('Constraints form is invalid:', this.constraintsForm.errors, this.constraintsForm.value);
        return;
      }
      console.log('Moving to review step. Constraints form value:', this.constraintsForm.value);
      this.currentStep.set('review');
    }
  }

  protected previousStep() {
    const current = this.currentStep();
    
    if (current === 'allocation') {
      this.currentStep.set('risk');
    } else if (current === 'constraints') {
      this.currentStep.set('allocation');
    } else if (current === 'review') {
      this.currentStep.set('constraints');
    }
  }

  protected applyAllocationPreset(preset: typeof this.allocationPresets[0]) {
    this.allocationForm.patchValue({
      equityTarget: preset.equity,
      fixedIncomeTarget: preset.fixedIncome,
      cashTarget: preset.cash
    });
  }

  protected savePreferences() {
    if (this.riskForm.invalid || this.allocationForm.invalid || this.constraintsForm.invalid) {
      return;
    }

    if (this.hasValidationErrors()) {
      this.error.set('Please fix validation errors before saving');
      return;
    }

    this.saving.set(true);
    this.error.set(null);

    const riskValues = this.riskForm.getRawValue();
    const allocationValues = this.allocationForm.getRawValue();
    const constraintValues = this.constraintsForm.getRawValue();

    const request: PreferenceUpdateRequest = {
      risk_profile: {
        risk_profile_id: this.currentPreferences()?.risk_profile?.risk_profile_id || `risk_${riskValues.riskLevel}`,
        risk_level: riskValues.riskLevel,
        max_single_position_pct: String(riskValues.maxSinglePositionPct),
        max_sector_pct: String(riskValues.maxSectorPct),
        allowed_asset_classes: riskValues.allowedAssetClasses
      },
      allocation_target: {
        asset_class_targets: {
          equity: String(allocationValues.equityTarget),
          fixed_income: String(allocationValues.fixedIncomeTarget),
          cash: String(allocationValues.cashTarget)
        },
        tolerance_bands: {
          equity: String(allocationValues.equityTolerance),
          fixed_income: String(allocationValues.fixedIncomeTolerance),
          cash: String(allocationValues.cashTolerance)
        }
      },
      constraints: {
        tax_strategy: constraintValues.taxStrategy,
        esg_preference: constraintValues.esgPreference,
        dividend_preference: constraintValues.dividendPreference,
        excluded_sectors: constraintValues.excludedSectors
      }
    };

    this.preferenceService.updatePreferences(this.clientId(), request).subscribe({
      next: (updated) => {
        this.currentPreferences.set(updated);
        this.saving.set(false);
        // Navigate back to main app
        this.router.navigate(['/']);
      },
      error: () => {
        this.error.set('Failed to save preferences');
        this.saving.set(false);
      }
    });
  }

  protected cancel() {
    this.router.navigate(['/']);
  }
}

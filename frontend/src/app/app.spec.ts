import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { App } from './app';
import { HealthService } from './core/api/health.service';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        {
          provide: HealthService,
          useValue: {
            getHealth: () =>
              of({
                status: 'ok',
                app: 'Asset Management API',
                environment: 'test',
                schema_version: '1.0.0',
                policy_version: '1.0.0'
              })
          }
        }
      ]
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render product shell', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Asset Management');
    expect(compiled.textContent).toContain('Advisory only');
  });
});

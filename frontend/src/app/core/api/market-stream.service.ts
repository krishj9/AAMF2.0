import { Injectable, NgZone, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval, startWith, switchMap } from 'rxjs';

import { apiUrl } from './api-config';
import { MarketStreamEvent } from './market.models';

@Injectable({ providedIn: 'root' })
export class MarketStreamService {
  private readonly http = inject(HttpClient);
  private readonly zone = inject(NgZone);

  stream(accountId?: string): Observable<MarketStreamEvent> {
    if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
      return this.pollMarketTicks(accountId);
    }

    return new Observable<MarketStreamEvent>((subscriber) => {
      if (typeof EventSource === 'undefined') {
        subscriber.complete();
        return undefined;
      }

      const params = new URLSearchParams({ limit: '0', interval_ms: '1500' });
      if (accountId) {
        params.set('account_id', accountId);
      }
      const source = new EventSource(apiUrl(`/market/stream?${params.toString()}`));
      source.onmessage = (message) => {
        this.zone.run(() => subscriber.next(JSON.parse(message.data) as MarketStreamEvent));
      };
      source.onerror = () => {
        this.zone.run(() => subscriber.error(new Error('Market stream disconnected.')));
        source.close();
      };

      return () => source.close();
    });
  }

  private pollMarketTicks(accountId?: string): Observable<MarketStreamEvent> {
    return interval(1500).pipe(
      startWith(0),
      switchMap(() => {
        const params = new URLSearchParams({ interval_ms: '1500' });
        if (accountId) {
          params.set('account_id', accountId);
        }
        return this.http.get<MarketStreamEvent>(apiUrl(`/market/tick?${params.toString()}`));
      })
    );
  }
}

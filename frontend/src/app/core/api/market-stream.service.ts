import { Injectable, NgZone, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { MarketStreamEvent } from './market.models';

@Injectable({ providedIn: 'root' })
export class MarketStreamService {
  private readonly zone = inject(NgZone);

  stream(): Observable<MarketStreamEvent> {
    return new Observable<MarketStreamEvent>((subscriber) => {
      if (typeof EventSource === 'undefined') {
        subscriber.complete();
        return undefined;
      }

      const source = new EventSource('/api/market/stream?limit=0&interval_ms=1500');
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
}

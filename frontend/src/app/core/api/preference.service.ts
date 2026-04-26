import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { apiUrl } from './api-config';
import { PreferenceHistoryItem, PreferenceProfile, PreferenceUpdateRequest } from './preference.models';

@Injectable({ providedIn: 'root' })
export class PreferenceService {
  private readonly http = inject(HttpClient);

  getPreferences(clientId: string): Observable<PreferenceProfile> {
    return this.http.get<PreferenceProfile>(apiUrl(`/preferences/${clientId}`));
  }

  updatePreferences(clientId: string, request: PreferenceUpdateRequest): Observable<PreferenceProfile> {
    return this.http.put<PreferenceProfile>(apiUrl(`/preferences/${clientId}`), request);
  }

  getPreferenceHistory(clientId: string): Observable<PreferenceHistoryItem[]> {
    return this.http.get<PreferenceHistoryItem[]>(apiUrl(`/preferences/${clientId}/history`));
  }
}

import { HttpInterceptorFn } from '@angular/common/http';

/**
 * Injects the x-api-token header on every outbound API request.
 * The token is read from window.assetManagementConfig.apiToken,
 * which is set in app-config.js at deploy time.
 * In local dev, app-config.js sets apiToken to '' so the gate is skipped.
 */
export const tokenInterceptor: HttpInterceptorFn = (req, next) => {
  const token = window.assetManagementConfig?.apiToken ?? '';
  if (!token) {
    return next(req);
  }
  return next(req.clone({ setHeaders: { 'x-api-token': token } }));
};

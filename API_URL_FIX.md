# API URL Fix for AWS Deployment

## Problem

When deployed to AWS, the frontend was making API calls without the `/api` prefix:
- ❌ `https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/preferences/client_demo` (404)
- ✅ `https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/api/preferences/client_demo` (works)

## Root Cause

The `apiUrl()` function in `frontend/src/app/core/api/api-config.ts` was not adding the `/api` prefix when using the full API Gateway URL.

**Before:**
```typescript
export function apiUrl(path: string): string {
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}/${path.replace(/^\//, '')}`;
}
```

This worked locally because:
- Local: `baseUrl = '/api'` (from proxy)
- Result: `/api/preferences/client_demo` ✅

But failed on AWS because:
- AWS: `baseUrl = 'https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com'`
- Result: `https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/preferences/client_demo` ❌

## Solution

Updated `apiUrl()` to automatically add `/api` prefix when using API Gateway URL:

**After:**
```typescript
export function apiUrl(path: string): string {
  const baseUrl = getApiBaseUrl();
  const cleanPath = path.replace(/^\//, '');
  
  // If using API Gateway URL (not local proxy), ensure /api prefix
  if (baseUrl.startsWith('http')) {
    // Add /api prefix if not already present in the path
    const pathWithApi = cleanPath.startsWith('api/') ? cleanPath : `api/${cleanPath}`;
    return `${baseUrl}/${pathWithApi}`;
  }
  
  // Local development with proxy - path already has /api from baseUrl
  return `${baseUrl}/${cleanPath}`;
}
```

## How It Works Now

### Local Development
- `baseUrl = '/api'` (from proxy.conf.json)
- `path = '/preferences/client_demo'`
- Result: `/api/preferences/client_demo` ✅

### AWS Deployment
- `baseUrl = 'https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com'`
- `path = '/preferences/client_demo'`
- Detects HTTP URL → adds `/api` prefix
- Result: `https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/api/preferences/client_demo` ✅

## Files Modified

- `frontend/src/app/core/api/api-config.ts` - Updated `apiUrl()` function

## Testing

### Test API Endpoints

```bash
# Health (no /api prefix)
curl https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/health

# Portfolios (with /api prefix)
curl https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/api/portfolios

# Preferences (with /api prefix)
curl https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/api/preferences/client_demo

# Market stream (with /api prefix)
curl -N https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com/api/market/stream
```

### Test Frontend

Open the frontend URL and verify:
1. ✅ Portfolio data loads
2. ✅ Market simulation stream works
3. ✅ Preferences page loads
4. ✅ Rebalance recommendations work

## Deployment

Frontend has been redeployed with the fix:

```bash
./infra/scripts/publish_frontend.sh \
  "https://r62c0mmp4i.execute-api.us-east-1.amazonaws.com" \
  "asset-management-dev-frontend-855603407942"
```

## Verification

Open your frontend:
```
http://asset-management-dev-frontend-855603407942.s3-website.us-east-2.amazonaws.com
```

Everything should now work correctly! 🎉

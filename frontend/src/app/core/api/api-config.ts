declare global {
  interface Window {
    assetManagementConfig?: {
      apiBaseUrl?: string;
    };
  }
}

/**
 * S3 static website hosting cannot reverse-proxy `/api` to API Gateway. The default
 * `apiBaseUrl: '/api'` in `app-config.js` is only for local `ng serve` (proxy).
 * On a `*.s3-website-*.amazonaws.com` host, you must set `apiBaseUrl` to the
 * Terraform `api_base_url` (Execute API) before uploading the build to S3.
 */
function isS3StaticWebsiteHost(hostname: string): boolean {
  return hostname.includes('s3-website-') && hostname.endsWith('.amazonaws.com');
}

function getApiBaseUrl(): string {
  const configured = window.assetManagementConfig?.apiBaseUrl;
  const resolved = (configured ?? '/api').replace(/\/$/, '');

  if (isS3StaticWebsiteHost(window.location.hostname)) {
    if (configured == null || configured === '/api') {
      const hint =
        "Set window.assetManagementConfig.apiBaseUrl in app-config.js to your API Gateway base URL, then re-upload. Example: `terraform output -raw api_base_url`.";
      throw new Error(
        `API base is still '/api' on S3 website hosting, so requests go to the static site, not API Gateway. ${hint}`,
      );
    }
  }

  return resolved;
}

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

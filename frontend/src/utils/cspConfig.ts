/**
 * Content Security Policy helper
 * Generates CSP headers for security
 */

export const cspConfig = {
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"], // Can be strict if you compile without inline
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", "data:", "https:"],
    fontSrc: ["'self'", "data:"],
    connectSrc: ["'self'", "https://api.example.com"], // Update with your actual API domain
    frameSrc: ["'none'"],
    objectSrc: ["'none'"],
    mediaSrc: ["'self'"],
    childSrc: ["'none'"],
    formAction: ["'self'"],
    baseUri: ["'self'"],
    manifestSrc: ["'self'"],
  },
};

/**
 * Generate CSP header string from config
 */
export function generateCSPHeader(
  directives: Record<string, string[]>
): string {
  return Object.entries(directives)
    .map(([key, values]) => {
      const directiveName = key
        .replace(/([A-Z])/g, "-$1")
        .toLowerCase()
        .slice(1);
      return `${directiveName} ${values.join(" ")}`;
    })
    .join("; ");
}

/**
 * CSP nonce generator for inline scripts
 * Use this to generate a nonce for inline scripts in your HTML
 */
export function generateNonce(): string {
  const chars =
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  let nonce = "";
  for (let i = 0; i < 32; i++) {
    nonce += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return nonce;
}

/**
 * Get CSP header string for the current environment
 * In production, use strict CSP. In development, allow inline for faster development
 */
export function getCSPHeader(isDevelopment: boolean = false): string {
  const config = { ...cspConfig.directives };

  if (isDevelopment) {
    // Relax CSP in development for faster iteration
    config.scriptSrc = ["'self'", "'unsafe-inline'", "'unsafe-eval'"];
    config.styleSrc = ["'self'", "'unsafe-inline'"];
  }

  return generateCSPHeader(config);
}

// For Vite or other dev servers, you can use this in vite.config.ts:
// Example middleware configuration:
/*
export default defineConfig({
  server: {
    middlewares: [
      {
        name: 'csp-header',
        apply: 'serve',
        enforce: 'pre',
        handler(req, res, next) {
          const cspHeader = getCSPHeader(true); // true for development
          res.setHeader('Content-Security-Policy', cspHeader);
          next();
        }
      }
    ]
  }
});
*/

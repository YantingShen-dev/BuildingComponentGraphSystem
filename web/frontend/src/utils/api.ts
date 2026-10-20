// One default API for local development; Vite proxies /api to the Python service.
export const API_URL = (import.meta.env.VITE_API_URL || '/api').replace(/\/+$/, '');
export const API_URL_OPT = (import.meta.env.VITE_API_URL_OPT || API_URL).replace(/\/+$/, '');

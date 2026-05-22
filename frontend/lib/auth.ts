const TOKEN_KEY = 'sentinel_token';
const USER_KEY  = 'sentinel_user';

export interface AuthUser {
  username: string;
  role: string;
}

export const saveAuth = (token: string, user: AuthUser) => {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USER_KEY, JSON.stringify(user));
};

export const getToken = (): string | null =>
  typeof window !== 'undefined' ? localStorage.getItem(TOKEN_KEY) : null;

export const getUser = (): AuthUser | null => {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
};

export const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

export const isAuthenticated = (): boolean => !!getToken();

export const authHeaders = (): Record<string, string> => {
  const token = getToken();
  return token
    ? { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    : { 'Content-Type': 'application/json' };
};

export const apiFetch = async (path: string, options: RequestInit = {}) => {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  // fallback API key for non-JWT calls
  headers['X-API-Key'] = 'soc_diploma_secret_2026';

  const res = await fetch(path, { ...options, headers });
  if (res.status === 401 || res.status === 403) {
    clearAuth();
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  return res;
};

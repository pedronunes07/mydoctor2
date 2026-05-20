/**
 * URL da API Django (mydoctor-api).
 * Ex.: http://127.0.0.1:8000 ou https://seu-projeto.vercel.app
 */
export function getApiBaseUrl(): string | null {
  const u = process.env.EXPO_PUBLIC_API_URL;
  if (typeof u === 'string' && u.trim().length > 0) {
    return u.replace(/\/$/, '');
  }
  return null;
}

export function isApiMode(): boolean {
  return getApiBaseUrl() !== null;
}

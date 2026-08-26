// Shared player utility functions extracted from feature components
// Used by: market, favorites, my-roster, calculator, clausulable, analytics/market

const PHOTO_BASE = 'https://static01.mondocore.com/futmondo/img/faces/64/';
const TEAM_LOGO_BASE = 'https://static02.mondocore.com/futmondo/img/teams/64/';

/** Default player avatar as a data URI (grey silhouette — close-up face like real photos) */
const DEFAULT_PLAYER_PHOTO = 'data:image/svg+xml;base64,' + btoa(`
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
  <rect width="64" height="64" fill="#e0e0e0" rx="32"/>
  <circle cx="32" cy="28" r="18" fill="#bdbdbd"/>
  <ellipse cx="32" cy="62" rx="20" ry="14" fill="#bdbdbd"/>
</svg>`);

/**
 * Returns the player photo URL from their slug.
 * If no slug provided, returns default avatar.
 */
export function getPlayerPhoto(slug: string): string {
  if (!slug) return DEFAULT_PLAYER_PHOTO;
  return `${PHOTO_BASE}${slug}.png`;
}

/**
 * Returns the team logo URL.
 * If no logo/id provided, returns empty string.
 */
export function getTeamLogo(logo: string): string {
  if (!logo) return '';
  return `${TEAM_LOGO_BASE}${logo}`;
}

/**
 * Maps a position string (Spanish) to a CSS class key.
 * Supports: delantero→fwd, centrocampista→mid, defensa→def, portero→gk.
 * Also handles English variants (forward, mid, defender, keeper).
 */
export function getPositionKey(position: string): string {
  const p = (position || '').toLowerCase();
  if (p.includes('delantero') || p.includes('forward')) return 'fwd';
  if (p.includes('centrocampista') || p.includes('medio') || p.includes('mid')) return 'mid';
  if (p.includes('defensa') || p.includes('defender')) return 'def';
  if (p.includes('portero') || p.includes('keeper')) return 'gk';
  return 'mid';
}

/**
 * Maps a position string (Spanish) to a short display label.
 * Returns: DL, MC, DF, PT, or the original position string as fallback.
 */
export function getPositionLabel(position: string): string {
  const p = (position || '').toLowerCase();
  if (p.includes('delantero')) return 'DL';
  if (p.includes('centrocampista')) return 'MC';
  if (p.includes('defensa')) return 'DF';
  if (p.includes('portero')) return 'PT';
  return position || '-';
}

/**
 * Image error handler: replaces broken image with default avatar.
 * Used as (error)="onImgError($event)" in templates.
 */
export function onImgError(event: Event): void {
  const img = event.target as HTMLImageElement;
  if (img.src !== DEFAULT_PLAYER_PHOTO) {
    img.src = DEFAULT_PLAYER_PHOTO;
  }
}

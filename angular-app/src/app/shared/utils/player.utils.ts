// Shared player utility functions extracted from feature components
// Used by: market, favorites, my-roster, calculator, clausulable, analytics/market

const PHOTO_BASE = 'https://static01.mondocore.com/futmondo/img/faces/64/';
const TEAM_LOGO_BASE = 'https://static02.mondocore.com/futmondo/img/teams/64/';

/**
 * Returns the player photo URL from their slug.
 * If no slug provided, returns empty string (components hide broken images via (error) handler).
 */
export function getPlayerPhoto(slug: string): string {
  if (!slug) return '';
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
 * Image error handler: hides the broken image element.
 * Used as (error)="onImgError($event)" in templates.
 */
export function onImgError(event: Event): void {
  (event.target as HTMLElement).style.display = 'none';
}

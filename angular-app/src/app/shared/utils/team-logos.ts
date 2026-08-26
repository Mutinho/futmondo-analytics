/**
 * Map of Futmondo team IDs to logo filenames.
 * Used as fallback when the API doesn't return team logos.
 */
export const TEAM_LOGO_MAP: Record<string, string> = {
  '504e581e4d8bec9a670000c6': 'real-madrid.png',
  '504e581e4d8bec9a670000c7': 'barcelona.png',
  '504e581e4d8bec9a670000c8': 'atletico-de-madrid.png',
  '504e581e4d8bec9a670000c9': 'athletic-de-bilbao.png',
  '504e581e4d8bec9a670000ca': 'rayo-vallecano.png',
  '504e581e4d8bec9a670000cb': 'valencia.png',
  '504e581e4d8bec9a670000cc': 'betis.png',
  '504e581e4d8bec9a670000cd': 'getafe.png',
  '504e581e4d8bec9a670000ce': 'real-sociedad.png',
  '504e581e4d8bec9a670000cf': 'levante.png',
  '504e581e4d8bec9a670000d0': 'espanyol.png',
  '504e581e4d8bec9a670000d1': 'osasuna.png',
  '504e581e4d8bec9a670000d5': 'sevilla.png',
  '504e581e4d8bec9a670000d6': 'malaga.png',
  '504e581e4d8bec9a670000d8': 'deportivo-de-la-coruna.png',
  '504e581e4d8bec9a670000d9': 'celta-de-vigo.png',
  '51b889b1e401a15f2c0000f0': 'elche.png',
  '51b890f5b986415a2c000012': 'villarreal.png',
  '52038563b8d07d930b00008a': 'deportivo-alaves.png',
  '520e4ee4a776cc826b00004b': 'racing-santander.png',
};

/**
 * Get team logo URL from team ID using the static map.
 */
export function getTeamLogoById(teamId: string): string {
  const logo = TEAM_LOGO_MAP[teamId];
  if (!logo) return '';
  return `https://static02.mondocore.com/futmondo/img/teams/64/${logo}`;
}

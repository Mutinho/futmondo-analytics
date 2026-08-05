export interface TeamEvolution {
  team_id: string;
  team_name: string;
  points_evolution: number[];
  positions_evolution: number[];
}

export interface EvolutionResponse {
  success: boolean;
  data: {
    matchdays: number[];
    teams: TeamEvolution[];
  };
  source?: string;
}

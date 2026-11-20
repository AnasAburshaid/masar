export interface SectionProgress {
  section_id: number;
  title: string;
  completed_topics: number;
  total_topics: number;
  percentage: number;
  is_complete: boolean;
}

export interface JourneyProgress {
  journey_id: number;
  title: string;
  completed_topics: number;
  total_topics: number;
  percentage: number;
  is_complete: boolean;
  sections: SectionProgress[];
}

export interface DashboardStats {
  totalJourneys: number;
  completedJourneys: number;
  inProgressJourneys: number;
  notStartedJourneys: number;
  totalTopics: number;
  completedTopics: number;
  inProgressTopics: number;
  overallPercentage: number;
}

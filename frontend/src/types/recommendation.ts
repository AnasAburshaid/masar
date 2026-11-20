export type RecommendationType =
  | 'next_topic'
  | 'knowledge_gap'
  | 'review_refresher'
  | 'prerequisite'
  | 'journey_update';

export interface Recommendation {
  title: string;
  reason: string;
  recommendation_type: RecommendationType;
  journey_id?: number | null;
  journey_title?: string | null;
  section_id?: number | null;
  suggested_action?: string | null;
  action_payload?: Record<string, unknown> | null;
  confidence: number;
  created_at: string;
}

export interface KnowledgeGap {
  topic_name: string;
  description: string;
  remedy: string;
  related_journey_id?: number | null;
  related_journey_title?: string | null;
}

export interface AdaptiveLearningSummary {
  user_id: number;
  total_completed_topics: number;
  total_in_progress_topics: number;
  active_journey_titles: string[];
  knowledge_gaps: KnowledgeGap[];
  recommendations: Recommendation[];
  generated_at: string;
}

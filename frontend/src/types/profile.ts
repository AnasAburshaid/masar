export type ProfileCategory =
  | 'skill'
  | 'technology'
  | 'language'
  | 'experience'
  | 'project'
  | 'knowledge'
  | 'goal';

export type SkillLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';

export type ProfileSourceType = 'manual' | 'document' | 'conversation';

export interface ProfileItem {
  id: number;
  user_id: number;
  category: ProfileCategory;
  name: string;
  level?: SkillLevel | null;
  is_confirmed: boolean;
  source_type: ProfileSourceType;
  source_id?: number | null;
  created_at: string;
  updated_at?: string | null;
}

export interface LearningProfile {
  user_id: number;
  bio: string;
  confirmed_items: ProfileItem[];
  inferred_items: ProfileItem[];
  total_items: number;
}

export interface ProfileItemCreatePayload {
  name: string;
  category: ProfileCategory;
  level?: SkillLevel | null;
  is_confirmed?: boolean;
}

export interface ProfileItemUpdatePayload {
  name?: string;
  category?: ProfileCategory;
  level?: SkillLevel | null;
  is_confirmed?: boolean;
}

export interface ProfileBioUpdatePayload {
  bio: string;
}

export interface ProfileExtractionResponse {
  extracted_items: ProfileItem[];
  source_type: string;
  source_id: number;
}

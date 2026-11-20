/**
 * Types and interfaces for Learning Journeys, Sections, Topics, and Notes.
 */

export interface Journey {
  id: number;
  title: string;
  description: string;
  user_id?: number | null;
  created_at?: string;
  updated_at?: string;
}

export interface JourneyCreatePayload {
  title: string;
  description: string;
}

export interface JourneyUpdatePayload {
  title?: string;
  description?: string;
}

export interface Section {
  id: number;
  journey_id: number;
  title: string;
  created_at?: string;
  updated_at?: string;
}

export interface SectionCreatePayload {
  journey_id: number;
  title: string;
}

export interface SectionUpdatePayload {
  title: string;
}

export interface Topic {
  id: number;
  section_id: number;
  title: string;
  is_completed: boolean;
  created_at?: string;
  updated_at?: string;
}

export interface TopicCreatePayload {
  section_id: number;
  title: string;
  is_completed?: boolean;
}

export interface TopicUpdatePayload {
  title?: string;
  is_completed?: boolean;
}

export interface Note {
  id: number;
  topic_id: number;
  content: string;
  created_at?: string;
  updated_at?: string;
}

export interface NoteCreatePayload {
  topic_id: number;
  content: string;
}

export interface NoteUpdatePayload {
  content: string;
}

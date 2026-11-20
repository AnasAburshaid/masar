import { apiClient } from './client';
import { Note, NoteCreatePayload, NoteUpdatePayload } from '@/types/journey';

export const noteService = {
  /**
   * List all notes attached to a topic (GET /topics/{topicId}/notes).
   */
  async listNotes(topicId: number): Promise<Note[]> {
    return apiClient.get<Note[]>(`/topics/${topicId}/notes`);
  },

  /**
   * Get a note by ID (GET /notes/{id}).
   */
  async getNote(noteId: number): Promise<Note> {
    return apiClient.get<Note>(`/notes/${noteId}`);
  },

  /**
   * Create a new note for a topic (POST /notes).
   */
  async createNote(payload: NoteCreatePayload): Promise<Note> {
    return apiClient.post<Note>('/notes', payload);
  },

  /**
   * Update note content (PUT /notes/{id}).
   */
  async updateNote(noteId: number, payload: NoteUpdatePayload): Promise<Note> {
    return apiClient.put<Note>(`/notes/${noteId}`, payload);
  },

  /**
   * Delete a note (DELETE /notes/{id}).
   */
  async deleteNote(noteId: number): Promise<void> {
    return apiClient.delete<void>(`/notes/${noteId}`);
  },
};

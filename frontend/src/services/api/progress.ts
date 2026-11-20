import { apiClient } from './client';
import { JourneyProgress, SectionProgress, DashboardStats } from '@/types/progress';

export const progressService = {
  /**
   * Fetch detailed learning progress for a specific journey (GET /journeys/{journey_id}/progress).
   */
  async getJourneyProgress(journeyId: number): Promise<JourneyProgress> {
    return apiClient.get<JourneyProgress>(`/journeys/${journeyId}/progress`);
  },

  /**
   * Fetch learning progress for a specific section (GET /sections/{section_id}/progress).
   */
  async getSectionProgress(sectionId: number): Promise<SectionProgress> {
    return apiClient.get<SectionProgress>(`/sections/${sectionId}/progress`);
  },

  /**
   * Aggregate statistics across multiple learning journey progress objects.
   */
  calculateDashboardStats(progressList: JourneyProgress[]): DashboardStats {
    if (!progressList || progressList.length === 0) {
      return {
        totalJourneys: 0,
        completedJourneys: 0,
        inProgressJourneys: 0,
        notStartedJourneys: 0,
        totalTopics: 0,
        completedTopics: 0,
        inProgressTopics: 0,
        overallPercentage: 0,
      };
    }

    const totalJourneys = progressList.length;
    let completedJourneys = 0;
    let inProgressJourneys = 0;
    let notStartedJourneys = 0;
    let totalTopics = 0;
    let completedTopics = 0;

    for (const p of progressList) {
      totalTopics += p.total_topics;
      completedTopics += p.completed_topics;

      if (p.total_topics > 0 && p.is_complete) {
        completedJourneys += 1;
      } else if (p.completed_topics > 0 && !p.is_complete) {
        inProgressJourneys += 1;
      } else {
        notStartedJourneys += 1;
      }
    }

    const inProgressTopics = Math.max(0, totalTopics - completedTopics);
    const overallPercentage =
      totalTopics > 0 ? Math.round((completedTopics / totalTopics) * 1000) / 10 : 0;

    return {
      totalJourneys,
      completedJourneys,
      inProgressJourneys,
      notStartedJourneys,
      totalTopics,
      completedTopics,
      inProgressTopics,
      overallPercentage,
    };
  },
};

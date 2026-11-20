import test from 'node:test';
import assert from 'node:assert/strict';
import { progressService } from './progress';
import { JourneyProgress } from '@/types/progress';

test('progressService.getJourneyProgress calls correct endpoint and parses payload', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedUrl = '';

  globalThis.fetch = (async (input: RequestInfo | URL) => {
    capturedUrl = String(input);
    const mockResponse: JourneyProgress = {
      journey_id: 5,
      title: 'Full-Stack Next.js',
      completed_topics: 8,
      total_topics: 10,
      percentage: 80.0,
      is_complete: false,
      sections: [
        {
          section_id: 1,
          title: 'App Router',
          completed_topics: 5,
          total_topics: 5,
          percentage: 100.0,
          is_complete: true,
        },
        {
          section_id: 2,
          title: 'Server Actions',
          completed_topics: 3,
          total_topics: 5,
          percentage: 60.0,
          is_complete: false,
        },
      ],
    };
    return new Response(JSON.stringify(mockResponse), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const result = await progressService.getJourneyProgress(5);
  assert.equal(result.journey_id, 5);
  assert.equal(result.percentage, 80.0);
  assert.equal(result.sections.length, 2);
  assert.ok(capturedUrl.includes('/journeys/5/progress'));
});

test('progressService.getSectionProgress calls correct endpoint and parses payload', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedUrl = '';

  globalThis.fetch = (async (input: RequestInfo | URL) => {
    capturedUrl = String(input);
    return new Response(
      JSON.stringify({
        section_id: 12,
        title: 'Concurrency',
        completed_topics: 4,
        total_topics: 4,
        percentage: 100.0,
        is_complete: true,
      }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }) as typeof fetch;

  const result = await progressService.getSectionProgress(12);
  assert.equal(result.section_id, 12);
  assert.equal(result.is_complete, true);
  assert.equal(result.percentage, 100.0);
  assert.ok(capturedUrl.includes('/sections/12/progress'));
});

test('progressService.calculateDashboardStats handles empty and populated progress lists', () => {
  // Empty array
  const emptyStats = progressService.calculateDashboardStats([]);
  assert.deepEqual(emptyStats, {
    totalJourneys: 0,
    completedJourneys: 0,
    inProgressJourneys: 0,
    notStartedJourneys: 0,
    totalTopics: 0,
    completedTopics: 0,
    inProgressTopics: 0,
    overallPercentage: 0,
  });

  // Populated array with various statuses
  const mockJourneys: JourneyProgress[] = [
    {
      journey_id: 1,
      title: 'Journey 1',
      completed_topics: 10,
      total_topics: 10,
      percentage: 100.0,
      is_complete: true,
      sections: [],
    },
    {
      journey_id: 2,
      title: 'Journey 2',
      completed_topics: 2,
      total_topics: 5,
      percentage: 40.0,
      is_complete: false,
      sections: [],
    },
    {
      journey_id: 3,
      title: 'Journey 3',
      completed_topics: 0,
      total_topics: 5,
      percentage: 0.0,
      is_complete: false,
      sections: [],
    },
  ];

  const stats = progressService.calculateDashboardStats(mockJourneys);
  assert.equal(stats.totalJourneys, 3);
  assert.equal(stats.completedJourneys, 1);
  assert.equal(stats.inProgressJourneys, 1);
  assert.equal(stats.notStartedJourneys, 1);
  assert.equal(stats.totalTopics, 20);
  assert.equal(stats.completedTopics, 12);
  assert.equal(stats.inProgressTopics, 8);
  assert.equal(stats.overallPercentage, 60.0); // 12 / 20 = 60.0%
});

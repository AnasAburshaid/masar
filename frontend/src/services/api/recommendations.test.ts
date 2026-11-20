import test from 'node:test';
import assert from 'node:assert/strict';
import { recommendationService } from './recommendations';

test('recommendationService fetches recommendations and proposes improvements', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedMethod = '';
  let capturedUrl = '';
  let capturedBody: unknown = null;

  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    capturedUrl = String(input);
    capturedMethod = init?.method || 'GET';
    capturedBody = init?.body;

    if (capturedMethod === 'GET' && capturedUrl.includes('/recommendations')) {
      return new Response(
        JSON.stringify({
          user_id: 1,
          total_completed_topics: 5,
          total_in_progress_topics: 3,
          active_journey_titles: ['Cloud Architecture'],
          knowledge_gaps: [
            {
              topic_name: 'Message Queues',
              description: 'Profile goal not covered in active roadmaps.',
              remedy: 'Add RabbitMQ or Kafka topic.',
            },
          ],
          recommendations: [
            {
              title: "Study 'Service Discovery' in Cloud Architecture",
              reason: 'Next pending topic in section.',
              recommendation_type: 'next_topic',
              journey_id: 2,
              journey_title: 'Cloud Architecture',
              confidence: 0.95,
              created_at: '2026-11-20T20:00:00Z',
            },
          ],
          generated_at: '2026-11-20T20:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'POST' && capturedUrl.includes('/recommendations/improve/2')) {
      return new Response(
        JSON.stringify([
          {
            title: 'Async Processing',
            reason: 'Addresses concurrency bottlenecks.',
            recommendation_type: 'journey_update',
            confidence: 0.9,
            created_at: '2026-11-20T20:00:00Z',
          },
        ]),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return new Response(JSON.stringify({ detail: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as unknown as typeof fetch;

  // 1. Fetch recommendations without filter
  const summary = await recommendationService.getRecommendations();
  assert.equal(summary.user_id, 1);
  assert.equal(summary.recommendations.length, 1);
  assert.equal(summary.knowledge_gaps.length, 1);
  assert.equal(summary.recommendations[0].title, "Study 'Service Discovery' in Cloud Architecture");

  // 2. Fetch recommendations with journey filter
  await recommendationService.getRecommendations(2);
  assert.match(capturedUrl, /journey_id=2/);

  // 3. Propose journey improvements
  const improvements = await recommendationService.proposeImprovements(2, 'Need async patterns');
  assert.equal(improvements.length, 1);
  assert.equal(improvements[0].title, 'Async Processing');
  assert.equal(capturedMethod, 'POST');
  assert.match(String(capturedBody), /Need async patterns/);
});

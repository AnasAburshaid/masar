import test from 'node:test';
import assert from 'node:assert/strict';
import { journeyService } from './journeys';
import { sectionService } from './sections';
import { topicService } from './topics';
import { noteService } from './notes';

test('journeyService CRUD requests format URLs and bodies correctly', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedMethod = '';
  let capturedUrl = '';

  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    capturedUrl = String(input);
    capturedMethod = init?.method || 'GET';
    if (capturedMethod === 'DELETE') {
      return new Response(null, { status: 204 });
    }
    return new Response(JSON.stringify([{ id: 1, title: 'Python Backend', description: 'FastAPI' }]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const journeys = await journeyService.listJourneys();
  assert.equal(journeys.length, 1);
  assert.equal(journeys[0].title, 'Python Backend');
  assert.ok(capturedUrl.includes('/journeys'));

  await journeyService.deleteJourney(1);
  assert.equal(capturedMethod, 'DELETE');
  assert.ok(capturedUrl.includes('/journeys/1'));
});

test('sectionService sends proper journey_id and title', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedBody = '';

  globalThis.fetch = (async (_input: RequestInfo | URL, init?: RequestInit) => {
    capturedBody = String(init?.body);
    return new Response(JSON.stringify({ id: 10, journey_id: 1, title: 'Async Section' }), {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const section = await sectionService.createSection({ journey_id: 1, title: 'Async Section' });
  assert.equal(section.id, 10);
  assert.equal(section.title, 'Async Section');
  assert.ok(capturedBody.includes('Async Section'));
});

test('topicService handles status toggling and creation', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedUrl = '';

  globalThis.fetch = (async (input: RequestInfo | URL) => {
    capturedUrl = String(input);
    return new Response(JSON.stringify({ id: 25, section_id: 10, title: 'Event Loop', is_completed: true }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const topic = await topicService.markCompleted(25);
  assert.equal(topic.is_completed, true);
  assert.ok(capturedUrl.includes('/topics/25/complete'));
});

test('noteService CRUD attaches notes to topics', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedUrl = '';

  globalThis.fetch = (async (input: RequestInfo | URL) => {
    capturedUrl = String(input);
    return new Response(JSON.stringify([{ id: 100, topic_id: 25, content: 'Coroutine note' }]), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const notes = await noteService.listNotes(25);
  assert.equal(notes.length, 1);
  assert.equal(notes[0].content, 'Coroutine note');
  assert.ok(capturedUrl.includes('/topics/25/notes'));
});

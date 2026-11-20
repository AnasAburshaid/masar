import test from 'node:test';
import assert from 'node:assert/strict';
import { conversationService } from './conversations';

test('conversationService CRUD and sendMessage format URLs and bodies correctly', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedMethod = '';
  let capturedUrl = '';
  let capturedBody = '';

  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    capturedUrl = String(input);
    capturedMethod = init?.method || 'GET';
    capturedBody = String(init?.body || '');

    if (capturedMethod === 'DELETE') {
      return new Response(null, { status: 204 });
    }
    if (capturedMethod === 'POST' && capturedUrl.includes('/messages')) {
      return new Response(
        JSON.stringify({
          user_message: {
            id: 1,
            conversation_id: 10,
            role: 'user',
            content: 'How do index scans work?',
            created_at: '2026-11-20T18:00:00Z',
          },
          assistant_message: {
            id: 2,
            conversation_id: 10,
            role: 'assistant',
            content: 'Index scans traverse B-Tree index pages.',
            created_at: '2026-11-20T18:00:02Z',
          },
        }),
        { status: 201, headers: { 'Content-Type': 'application/json' } }
      );
    }
    if (capturedMethod === 'POST') {
      return new Response(
        JSON.stringify({
          id: 10,
          user_id: 1,
          title: 'PostgreSQL Internals',
          created_at: '2026-11-20T18:00:00Z',
          updated_at: '2026-11-20T18:00:00Z',
        }),
        { status: 201, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return new Response(
      JSON.stringify([
        {
          id: 10,
          user_id: 1,
          title: 'PostgreSQL Internals',
          created_at: '2026-11-20T18:00:00Z',
          updated_at: '2026-11-20T18:00:00Z',
        },
      ]),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  }) as typeof fetch;

  // 1. List conversations
  const list = await conversationService.listConversations();
  assert.equal(list.length, 1);
  assert.equal(list[0].title, 'PostgreSQL Internals');
  assert.ok(capturedUrl.includes('/conversations'));

  // 2. Create conversation
  const created = await conversationService.createConversation({ title: 'PostgreSQL Internals' });
  assert.equal(created.id, 10);
  assert.ok(capturedBody.includes('PostgreSQL Internals'));

  // 3. Send message
  const result = await conversationService.sendMessage(10, { content: 'How do index scans work?' });
  assert.equal(result.user_message.role, 'user');
  assert.equal(result.assistant_message.role, 'assistant');
  assert.ok(capturedUrl.includes('/conversations/10/messages'));
  assert.ok(capturedBody.includes('How do index scans work?'));

  // 4. Delete conversation
  await conversationService.deleteConversation(10);
  assert.equal(capturedMethod, 'DELETE');
  assert.ok(capturedUrl.includes('/conversations/10'));
});

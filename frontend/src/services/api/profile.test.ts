import test from 'node:test';
import assert from 'node:assert/strict';
import { profileService } from './profile';

test('profileService retrieves profile, updates bio, adds, updates, confirms, and deletes items', async (t) => {
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

    if (capturedMethod === 'DELETE') {
      return new Response(null, { status: 204 });
    }

    if (capturedMethod === 'GET' && capturedUrl.endsWith('/profile')) {
      return new Response(
        JSON.stringify({
          user_id: 1,
          bio: 'Senior Backend Engineer',
          confirmed_items: [
            {
              id: 10,
              user_id: 1,
              category: 'language',
              name: 'Python',
              level: 'advanced',
              is_confirmed: true,
              source_type: 'manual',
              created_at: '2026-11-20T20:00:00Z',
            },
          ],
          inferred_items: [
            {
              id: 11,
              user_id: 1,
              category: 'technology',
              name: 'Docker',
              level: 'intermediate',
              is_confirmed: false,
              source_type: 'document',
              source_id: 5,
              created_at: '2026-11-20T20:00:00Z',
            },
          ],
          total_items: 2,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'PUT' && capturedUrl.endsWith('/profile/bio')) {
      return new Response(
        JSON.stringify({
          user_id: 1,
          bio: 'Updated Bio Content',
          confirmed_items: [],
          inferred_items: [],
          total_items: 0,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'POST' && capturedUrl.endsWith('/profile/items')) {
      return new Response(
        JSON.stringify({
          id: 12,
          user_id: 1,
          category: 'skill',
          name: 'Distributed Systems',
          level: 'intermediate',
          is_confirmed: true,
          source_type: 'manual',
          created_at: '2026-11-20T20:00:00Z',
        }),
        { status: 201, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'PUT' && capturedUrl.includes('/profile/items/12')) {
      return new Response(
        JSON.stringify({
          id: 12,
          user_id: 1,
          category: 'skill',
          name: 'Distributed Systems',
          level: 'expert',
          is_confirmed: true,
          source_type: 'manual',
          created_at: '2026-11-20T20:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'POST' && capturedUrl.includes('/profile/items/11/confirm')) {
      return new Response(
        JSON.stringify({
          id: 11,
          user_id: 1,
          category: 'technology',
          name: 'Docker',
          level: 'intermediate',
          is_confirmed: true,
          source_type: 'document',
          source_id: 5,
          created_at: '2026-11-20T20:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'POST' && capturedUrl.includes('/profile/extract/document/5')) {
      return new Response(
        JSON.stringify({
          extracted_items: [
            {
              id: 11,
              user_id: 1,
              category: 'technology',
              name: 'Docker',
              level: 'intermediate',
              is_confirmed: false,
              source_type: 'document',
              source_id: 5,
              created_at: '2026-11-20T20:00:00Z',
            },
          ],
          source_type: 'document',
          source_id: 5,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return new Response(JSON.stringify({ detail: 'Not found' }), {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as unknown as typeof fetch;

  // 1. Get profile
  const profile = await profileService.getProfile();
  assert.equal(profile.user_id, 1);
  assert.equal(profile.confirmed_items.length, 1);
  assert.equal(profile.inferred_items.length, 1);
  assert.equal(profile.total_items, 2);

  // 2. Update bio
  const updatedBio = await profileService.updateBio('Updated Bio Content');
  assert.equal(updatedBio.bio, 'Updated Bio Content');
  assert.equal(capturedMethod, 'PUT');
  assert.match(String(capturedBody), /Updated Bio Content/);

  // 3. Add item
  const added = await profileService.addItem({
    name: 'Distributed Systems',
    category: 'skill',
    level: 'intermediate',
  });
  assert.equal(added.id, 12);
  assert.equal(added.name, 'Distributed Systems');
  assert.equal(capturedMethod, 'POST');

  // 4. Update item
  const updated = await profileService.updateItem(12, { level: 'expert' });
  assert.equal(updated.level, 'expert');
  assert.equal(capturedMethod, 'PUT');

  // 5. Confirm item
  const confirmed = await profileService.confirmItem(11);
  assert.equal(confirmed.is_confirmed, true);
  assert.equal(capturedMethod, 'POST');

  // 6. Delete item
  await profileService.deleteItem(12);
  assert.equal(capturedMethod, 'DELETE');
  assert.match(capturedUrl, /\/profile\/items\/12$/);

  // 7. Extract from document
  const extracted = await profileService.extractFromDocument(5);
  assert.equal(extracted.extracted_items.length, 1);
  assert.equal(extracted.source_id, 5);
});

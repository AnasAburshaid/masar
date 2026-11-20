import test from 'node:test';
import assert from 'node:assert/strict';
import { authService } from './auth';

test('authService.register sends POST /auth/register payload', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedPath = '';
  let capturedBody = '';

  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    capturedPath = String(input);
    capturedBody = String(init?.body);
    return new Response(
      JSON.stringify({ id: 1, email: 'newdev@example.com', is_active: true }),
      {
        status: 201,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }) as typeof fetch;

  const user = await authService.register({
    email: 'newdev@example.com',
    password: 'Password123!',
  });

  assert.equal(user.id, 1);
  assert.equal(user.email, 'newdev@example.com');
  assert.ok(capturedPath.includes('/auth/register'));
  assert.ok(capturedBody.includes('newdev@example.com'));
});

test('authService.login receives JWT token', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  globalThis.fetch = (async () => {
    return new Response(
      JSON.stringify({ access_token: 'mock.jwt.token', token_type: 'bearer' }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }) as typeof fetch;

  const result = await authService.login({
    email: 'dev@example.com',
    password: 'ValidPassword123!',
  });

  assert.equal(result.access_token, 'mock.jwt.token');
  assert.equal(result.token_type, 'bearer');
});

test('authService.getCurrentUser fetches /auth/me with bearer token', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let authHeader = '';

  globalThis.fetch = (async (_input: RequestInfo | URL, init?: RequestInit) => {
    const headers = new Headers(init?.headers);
    authHeader = headers.get('Authorization') || '';
    return new Response(
      JSON.stringify({ id: 42, email: 'authed@example.com', is_active: true }),
      {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }) as typeof fetch;

  const user = await authService.getCurrentUser('custom-jwt-token');
  assert.equal(user.id, 42);
  assert.equal(user.email, 'authed@example.com');
  assert.equal(authHeader, 'Bearer custom-jwt-token');
});

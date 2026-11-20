import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiClient } from './client';

test('ApiClient normalizes base URL correctly', () => {
  const client1 = new ApiClient('http://localhost:8000/');
  assert.ok(client1);

  const client2 = new ApiClient('http://localhost:8000');
  assert.ok(client2);
});

test('ApiClient formats query parameters properly in requests', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedUrl = '';
  let capturedHeaders: Headers | undefined;

  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    capturedUrl = String(input);
    capturedHeaders = init?.headers ? new Headers(init.headers) : undefined;
    return new Response(JSON.stringify({ status: 'ok' }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const client = new ApiClient('http://localhost:8000');
  client.setTokenProvider(() => 'test-bearer-token');

  const result = await client.get<{ status: string }>('/health', {
    params: { env: 'testing', count: 5 },
  });

  assert.deepEqual(result, { status: 'ok' });
  assert.ok(capturedUrl.includes('/health?env=testing&count=5'));
  assert.equal(capturedHeaders?.get('Authorization'), 'Bearer test-bearer-token');
  assert.equal(capturedHeaders?.get('Accept'), 'application/json');
});

test('ApiClient maps 401 response to ApiError', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  globalThis.fetch = (async () => {
    return new Response(JSON.stringify({ detail: 'Invalid credentials.' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const client = new ApiClient('http://localhost:8000');

  await assert.rejects(
    async () => {
      await client.post('/auth/login', { email: 'wrong@test.com', password: 'bad' });
    },
    (err: unknown) => {
      const isApiError = err instanceof Error && 'status' in err && (err as { status: number }).status === 401;
      return isApiError;
    }
  );
});

test('ApiClient passes FormData untouched in post without application/json Content-Type', async (t) => {
  const originalFetch = globalThis.fetch;
  t.after(() => {
    globalThis.fetch = originalFetch;
  });

  let capturedBody: unknown = null;
  let capturedHeaders: Headers | undefined;

  globalThis.fetch = (async (_input: RequestInfo | URL, init?: RequestInit) => {
    capturedBody = init?.body;
    capturedHeaders = init?.headers ? new Headers(init.headers) : undefined;
    return new Response(JSON.stringify({ id: 1 }), {
      status: 201,
      headers: { 'Content-Type': 'application/json' },
    });
  }) as typeof fetch;

  const client = new ApiClient('http://localhost:8000');
  const formData = new FormData();
  formData.append('test', 'value');

  const res = await client.post<{ id: number }>('/upload', formData);
  assert.equal(res.id, 1);
  assert.ok(capturedBody instanceof FormData);
  assert.equal(capturedHeaders?.has('Content-Type'), false);
});


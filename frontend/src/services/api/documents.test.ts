import test from 'node:test';
import assert from 'node:assert/strict';
import { documentService } from './documents';

test('documentService uploads, lists, retrieves, summarizes and deletes documents', async (t) => {
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

    if (capturedMethod === 'POST' && capturedUrl.includes('/upload')) {
      return new Response(
        JSON.stringify({
          id: 42,
          user_id: 1,
          filename: 'resume.pdf',
          file_type: 'pdf',
          file_size_bytes: 4096,
          file_size_display: '4.0 KB',
          summary: null,
          created_at: '2026-11-20T20:00:00Z',
        }),
        { status: 201, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'POST' && capturedUrl.includes('/summarize')) {
      return new Response(
        JSON.stringify({
          id: 42,
          filename: 'resume.pdf',
          summary: 'Executive Summary: Senior backend engineer.',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    if (capturedMethod === 'GET' && capturedUrl.includes('/documents/42')) {
      return new Response(
        JSON.stringify({
          id: 42,
          user_id: 1,
          filename: 'resume.pdf',
          file_type: 'pdf',
          file_size_bytes: 4096,
          file_size_display: '4.0 KB',
          extracted_text: 'Full extracted text content.',
          summary: null,
          created_at: '2026-11-20T20:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } }
      );
    }

    return new Response(
      JSON.stringify([
        {
          id: 42,
          user_id: 1,
          filename: 'resume.pdf',
          file_type: 'pdf',
          file_size_bytes: 4096,
          created_at: '2026-11-20T20:00:00Z',
        },
      ]),
      { status: 200, headers: { 'Content-Type': 'application/json' } }
    );
  }) as typeof fetch;

  // 1. Upload
  const fakeFile = new File(['dummy content'], 'resume.pdf', { type: 'application/pdf' });
  const uploaded = await documentService.uploadDocument(fakeFile);
  assert.ok(capturedBody);
  assert.equal(capturedMethod, 'POST');
  assert.match(capturedUrl, /\/documents\/upload$/);
  assert.equal(uploaded.id, 42);
  assert.equal(uploaded.filename, 'resume.pdf');

  // 2. List
  const list = await documentService.listDocuments();
  assert.equal(capturedMethod, 'GET');
  assert.match(capturedUrl, /\/documents$/);
  assert.equal(list.length, 1);
  assert.equal(list[0].id, 42);

  // 3. Get Detail
  const detail = await documentService.getDocument(42);
  assert.equal(capturedMethod, 'GET');
  assert.match(capturedUrl, /\/documents\/42$/);
  assert.equal(detail.extracted_text, 'Full extracted text content.');

  // 4. Summarize
  const summary = await documentService.summarizeDocument(42);
  assert.equal(capturedMethod, 'POST');
  assert.match(capturedUrl, /\/documents\/42\/summarize$/);
  assert.equal(summary.summary, 'Executive Summary: Senior backend engineer.');

  // 5. Delete
  await documentService.deleteDocument(42);
  assert.equal(capturedMethod, 'DELETE');
  assert.match(capturedUrl, /\/documents\/42$/);
});

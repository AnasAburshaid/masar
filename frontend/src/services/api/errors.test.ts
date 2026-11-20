import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiError } from './errors';

test('ApiError initializes correctly with defaults', () => {
  const err = new ApiError({
    message: 'Something went wrong',
    status: 400,
    detail: 'Bad request detail',
  });

  assert.equal(err.message, 'Something went wrong');
  assert.equal(err.status, 400);
  assert.equal(err.detail, 'Bad request detail');
  assert.equal(err.isNetworkError, false);
  assert.equal(err.userMessage, 'Bad request detail');
});

test('ApiError handles network error factory', () => {
  const err = ApiError.networkError(new Error('Connection refused'));

  assert.equal(err.status, 0);
  assert.equal(err.isNetworkError, true);
  assert.ok(err.userMessage.includes('Unable to connect'));
});

test('ApiError helper flags identify HTTP status codes', () => {
  const unauth = new ApiError({ message: 'Unauthorized', status: 401 });
  assert.equal(unauth.isUnauthorized, true);
  assert.equal(unauth.isForbidden, false);

  const forbidden = new ApiError({ message: 'Forbidden', status: 403 });
  assert.equal(forbidden.isForbidden, true);
  assert.equal(forbidden.isUnauthorized, false);

  const notFound = new ApiError({ message: 'Not Found', status: 404 });
  assert.equal(notFound.isNotFound, true);

  const validation = new ApiError({ message: 'Unprocessable', status: 422 });
  assert.equal(validation.isValidationError, true);
});

test('ApiError parses response detail properly', async () => {
  const mockResponse = new Response(
    JSON.stringify({ detail: 'Journey not found with id 999' }),
    {
      status: 404,
      headers: { 'Content-Type': 'application/json' },
    }
  );

  const apiError = await ApiError.fromResponse(mockResponse);
  assert.equal(apiError.status, 404);
  assert.equal(apiError.detail, 'Journey not found with id 999');
  assert.equal(apiError.userMessage, 'Journey not found with id 999');
});

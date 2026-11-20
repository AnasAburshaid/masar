import test from 'node:test';
import assert from 'node:assert/strict';
import { actionService } from './actions';
import { apiClient } from './client';

test('actionService.listProposals formats endpoint path correctly', async () => {
  const originalGet = apiClient.get;
  let capturedUrl = '';
  apiClient.get = async (url: string) => {
    capturedUrl = url;
    return [] as never;
  };

  try {
    const result = await actionService.listProposals(42);
    assert.equal(capturedUrl, '/conversations/42/proposals');
    assert.deepEqual(result, []);
  } finally {
    apiClient.get = originalGet;
  }
});

test('actionService.getProposal formats endpoint path correctly', async () => {
  const originalGet = apiClient.get;
  let capturedUrl = '';
  apiClient.get = async (url: string) => {
    capturedUrl = url;
    return { id: 7, title: 'Test Proposal' } as never;
  };

  try {
    const result = await actionService.getProposal(42, 7);
    assert.equal(capturedUrl, '/conversations/42/proposals/7');
    assert.equal(result.id, 7);
  } finally {
    apiClient.get = originalGet;
  }
});

test('actionService.approveProposal issues POST to approve endpoint', async () => {
  const originalPost = apiClient.post;
  let capturedUrl = '';
  apiClient.post = async (url: string) => {
    capturedUrl = url;
    return {
      proposal: { id: 7, status: 'executed' },
      message: 'Done',
      executed_count: 2,
      failed_count: 0,
    } as never;
  };

  try {
    const result = await actionService.approveProposal(42, 7);
    assert.equal(capturedUrl, '/conversations/42/proposals/7/approve');
    assert.equal(result.executed_count, 2);
    assert.equal(result.proposal.status, 'executed');
  } finally {
    apiClient.post = originalPost;
  }
});

test('actionService.rejectProposal issues POST to reject endpoint', async () => {
  const originalPost = apiClient.post;
  let capturedUrl = '';
  apiClient.post = async (url: string) => {
    capturedUrl = url;
    return { id: 7, status: 'rejected' } as never;
  };

  try {
    const result = await actionService.rejectProposal(42, 7);
    assert.equal(capturedUrl, '/conversations/42/proposals/7/reject');
    assert.equal(result.status, 'rejected');
  } finally {
    apiClient.post = originalPost;
  }
});

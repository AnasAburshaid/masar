export type ProposalStatus = 'pending' | 'approved' | 'rejected' | 'executed' | 'failed';

export interface ProposedAction {
  tool: string;
  parameters: Record<string, unknown>;
  description?: string;
  is_destructive?: boolean;
}

export interface ActionResult {
  action_index: number;
  tool: string;
  status: 'success' | 'failure';
  data?: Record<string, unknown> | null;
  error?: string | null;
}

export interface ActionProposal {
  id: number;
  conversation_id: number;
  user_id: number;
  title: string;
  status: ProposalStatus;
  has_destructive_actions: boolean;
  actions: ProposedAction[];
  results: ActionResult[];
  created_at: string;
  resolved_at?: string | null;
}

export interface ActionApprovalResponse {
  proposal: ActionProposal;
  message: string;
  executed_count: number;
  failed_count: number;
}

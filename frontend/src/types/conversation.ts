export type MessageRole = 'user' | 'assistant' | 'system';

export interface ConversationMessage {
  id: number;
  conversation_id: number;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: ConversationMessage[];
}

export interface CreateConversationPayload {
  title?: string;
}

export interface UpdateConversationPayload {
  title: string;
}

export interface SendMessagePayload {
  content: string;
}

export interface SendMessageResponse {
  user_message: ConversationMessage;
  assistant_message: ConversationMessage;
}

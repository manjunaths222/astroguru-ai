export interface User {
  id: number;
  email: string;
  name: string;
  picture_url?: string;
  type: 'user' | 'admin';
}

export interface Order {
  id: number;
  user_id: number;
  status: 'payment_pending' | 'processing' | 'completed' | 'failed' | 'refunded';
  type: 'full_report' | 'query';
  amount: number;
  birth_details?: BirthDetails;
  analysis_data?: any;
  error_reason?: string;
  created_at: string;
  updated_at: string;
}

export interface BirthDetails {
  name: string;
  dateOfBirth?: string;
  date_of_birth?: string;
  timeOfBirth?: string;
  time_of_birth?: string;
  placeOfBirth?: string;
  place_of_birth?: string;
  latitude?: number;
  longitude?: number;
  goals?: string[];
  user_query?: string;
}

export interface Payment {
  id: number;
  order_id: number;
  razorpay_order_id: string;
  razorpay_payment_id?: string;
  amount: number;
  status: 'pending' | 'success' | 'failed';
  payment_method?: string;
  razorpay_refund_id?: string;
  refund_amount?: number;
  refund_status?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: number;
  order_id: number;
  message_number: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ChatHistory {
  messages: ChatMessage[];
  message_count: number;
  messages_remaining: number;
  can_continue: boolean;
}

export interface PaymentCreateResponse {
  order_id: number;
  razorpay_order_id: string;
  amount: number;
  key_id: string;
  currency: string;
}


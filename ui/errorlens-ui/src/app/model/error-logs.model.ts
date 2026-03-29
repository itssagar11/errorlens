export interface ErrorBreakdown {
  status_code: number;
  count: number;
}

export interface ApiErrorData {
  api: string;
  total_errors: number;
  error_breakdown: ErrorBreakdown[];
}

export interface ErrorLogsResponse {
  service: string;
  start_time: string;
  end_time: string;
  total_apis_affected: number;
  total_errors: number;
  data: ApiErrorData[];
}

export interface ErrorTransaction {
  txn_id: string;
  timestamp: string;
  error: string | null;
  status_code: number | null;
}

export interface ErrorDetailsResponse {
  count: number;
  transactions: ErrorTransaction[];
}

export interface RawTraceGroup {
  service: string;
  logs: string[];
}

export interface RawTraceResponse {
  txn_id: string;
  raw_logs: RawTraceGroup[];
}

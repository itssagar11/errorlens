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

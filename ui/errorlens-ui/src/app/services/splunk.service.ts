import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { AiAnalysisResponse, ErrorDetailsResponse, ErrorLogsResponse, RawTraceResponse } from '../model/error-logs.model';

@Injectable({
  providedIn: 'root'
})
export class SplunkService {
  _endpoint: string = 'http://localhost:8001/';
  _backendEndpoint: string = 'http://localhost:8083/';
  constructor(private httpClient: HttpClient) {

   }


  getServices() {
    return this.httpClient.get(this._endpoint + 'get/services');
  }

  getErrorLogs(service: string, startTime: string, endTime: string): Observable<ErrorLogsResponse> {
    return this.httpClient.get<ErrorLogsResponse>(this._endpoint + `splunk/error?service=${service}&start_time=${encodeURIComponent(startTime)}&end_time=${encodeURIComponent(endTime)}`);
  }

  getErrorDetails(service: string, endpoint: string, statusCode?: number): Observable<ErrorDetailsResponse> {
    let url = `${this._endpoint}splunk/errors/details?service=${encodeURIComponent(service)}&endpoint=${encodeURIComponent(endpoint)}`;

    if (statusCode !== undefined) {
      url += `&status_code=${statusCode}`;
    }

    return this.httpClient.get<ErrorDetailsResponse>(url);
  }

  getRawTrace(txnId: string, service?: string): Observable<RawTraceResponse> {
    let url = `${this._endpoint}splunk/raw-trace/${encodeURIComponent(txnId)}`;

    if (service) {
      url += `?service=${encodeURIComponent(service)}`;
    }

    return this.httpClient.get<RawTraceResponse>(url);
  }

  analyseTraceWithAI(service: string, endpoint: string, txnId: string, trace?: RawTraceResponse): Observable<AiAnalysisResponse> {
    return this.httpClient.post<AiAnalysisResponse>(this._backendEndpoint + 'api/analyse-ai', {
      service,
      endpoint,
      txn_id: txnId,
      trace
    });
  }

}

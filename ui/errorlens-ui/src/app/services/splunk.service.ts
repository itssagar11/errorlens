import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ErrorDetailsResponse, ErrorLogsResponse, RawTraceResponse } from '../model/error-logs.model';

@Injectable({
  providedIn: 'root'
})
export class SplunkService {
  _endpoint: string = 'http://localhost:8001/';
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

  getRawTrace(txnId: string): Observable<RawTraceResponse> {
    return this.httpClient.get<RawTraceResponse>(this._endpoint + `splunk/raw-trace/${encodeURIComponent(txnId)}`);
  }

}

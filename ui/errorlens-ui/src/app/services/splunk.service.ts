import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ErrorLogsResponse } from '../model/error-logs.model';

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

}

import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { SearchBarComponent } from '../../component/search-bar/search-bar.component';
import { ErrorLensComponent } from '../../component/error-lens/error-lens.component';
import { ErrorLogsResponse } from '../../model/error-logs.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [SearchBarComponent, ErrorLensComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.css'
})
export class DashboardComponent {
  errorLogs: ErrorLogsResponse | null = null;

  constructor(private router: Router) {}

  onAnalysisComplete(data: ErrorLogsResponse): void {
    this.errorLogs = data;
  }

  openStatusDetails(payload: { service: string; endpoint: string; statusCode: number }): void {
    const urlTree = this.router.createUrlTree(['/drilldown'], {
      queryParams: {
        service: payload.service,
        endpoint: payload.endpoint,
        statusCode: payload.statusCode
      }
    });

    window.open(this.router.serializeUrl(urlTree), '_blank');
  }
}

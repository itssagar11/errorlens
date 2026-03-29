import { Component } from '@angular/core';
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

  onAnalysisComplete(data: ErrorLogsResponse): void {
    this.errorLogs = data;
  }
}

import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ErrorLogsResponse } from '../../model/error-logs.model';
import { TableRowComponent } from './utility/table-row/table-row.component';

@Component({
  selector: 'app-error-lens',
  standalone: true,
  imports: [CommonModule, TableRowComponent],
  templateUrl: './error-lens.component.html',
  styleUrl: './error-lens.component.css'
})
export class ErrorLensComponent {
  @Input() errorLogs: ErrorLogsResponse | null = null;
  @Output() statusSelected = new EventEmitter<{ service: string; endpoint: string; statusCode: number }>();

  get maxErrors(): number {
    if (!this.errorLogs?.data?.length) {
      return 0;
    }

    return Math.max(...this.errorLogs.data.map((item) => item.total_errors));
  }

  formatDate(dateValue: string | undefined): string {
    if (!dateValue) {
      return '-';
    }

    return new Date(dateValue).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  }

  onStatusSelected(payload: { endpoint: string; statusCode: number }): void {
    if (!this.errorLogs) {
      return;
    }

    this.statusSelected.emit({
      service: this.errorLogs.service,
      endpoint: payload.endpoint,
      statusCode: payload.statusCode
    });
  }
}

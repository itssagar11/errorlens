import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ApiErrorData, ErrorBreakdown } from '../../../../model/error-logs.model';

@Component({
  selector: 'tr[app-table-row]',
  standalone: true,
  imports: [],
  templateUrl: './table-row.component.html',
  styleUrl: './table-row.component.css'
})
export class TableRowComponent {
  @Input({ required: true }) row!: ApiErrorData;
  @Input() maxErrors = 0;
  @Output() statusSelected = new EventEmitter<{ endpoint: string; statusCode: number }>();

  get impactWidth(): number {
    if (!this.maxErrors) {
      return 0;
    }

    return Math.max(8, Math.round((this.row.total_errors / this.maxErrors) * 100));
  }

  openStatusDetails(error: ErrorBreakdown): void {
    this.statusSelected.emit({
      endpoint: this.row.api,
      statusCode: error.status_code
    });
  }
}

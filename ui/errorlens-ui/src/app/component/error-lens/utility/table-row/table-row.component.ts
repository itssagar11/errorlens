import { Component, Input } from '@angular/core';
import { ApiErrorData } from '../../../../model/error-logs.model';

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

  get impactWidth(): number {
    if (!this.maxErrors) {
      return 0;
    }

    return Math.max(8, Math.round((this.row.total_errors / this.maxErrors) * 100));
  }
}

import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { SplunkService } from '../../services/splunk.service';
import { ErrorDetailsResponse, RawTraceResponse } from '../../model/error-logs.model';

@Component({
  selector: 'app-drilldown',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './drilldown.component.html',
  styleUrl: './drilldown.component.css'
})
export class DrilldownComponent implements OnInit {
  service = '';
  endpoint = '';
  statusCode: number | null = null;
  selectedTxnId: string | null = null;

  details: ErrorDetailsResponse | null = null;
  trace: RawTraceResponse | null = null;

  isLoadingDetails = false;
  isLoadingTrace = false;
  detailsError = '';
  traceError = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private splunkService: SplunkService
  ) {}

  ngOnInit(): void {
    this.route.queryParamMap.subscribe((params) => {
      this.service = params.get('service') ?? '';
      this.endpoint = params.get('endpoint') ?? '';

      const statusCode = params.get('statusCode');
      this.statusCode = statusCode ? Number(statusCode) : null;
      this.selectedTxnId = params.get('txnId');

      this.loadDetails();

      if (this.selectedTxnId) {
        this.loadTrace(this.selectedTxnId);
      } else {
        this.trace = null;
        this.traceError = '';
      }
    });
  }

  loadDetails(): void {
    if (!this.service || !this.endpoint) {
      this.details = null;
      this.detailsError = 'Missing service or endpoint details.';
      return;
    }

    this.isLoadingDetails = true;
    this.detailsError = '';

    this.splunkService.getErrorDetails(this.service, this.endpoint, this.statusCode ?? undefined).subscribe({
      next: (data) => {
        this.details = data;
        this.isLoadingDetails = false;
      },
      error: () => {
        this.details = null;
        this.detailsError = 'Unable to load transaction IDs for this status code.';
        this.isLoadingDetails = false;
      }
    });
  }

  loadTrace(txnId: string): void {
    this.isLoadingTrace = true;
    this.traceError = '';

    this.splunkService.getRawTrace(txnId).subscribe({
      next: (data) => {
        this.trace = data;
        this.isLoadingTrace = false;
      },
      error: () => {
        this.trace = null;
        this.traceError = 'Unable to load raw logs for this transaction.';
        this.isLoadingTrace = false;
      }
    });
  }

  selectTxn(txnId: string): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { txnId },
      queryParamsHandling: 'merge'
    });
  }
}

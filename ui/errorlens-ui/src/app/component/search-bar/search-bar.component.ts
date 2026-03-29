import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SplunkService } from '../../services/splunk.service';
import { ErrorLogsResponse } from '../../model/error-logs.model';

@Component({
  selector: 'app-search-bar',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './search-bar.component.html',
  styleUrl: './search-bar.component.css'
})
export class SearchBarComponent implements OnInit {
  @Output() analysisComplete = new EventEmitter<ErrorLogsResponse>();

  services: string[]
  selectedService: string = '';
  dateRange: any = [{
    label: 'Last 15 mins',
    value: '15'
  },
  {
    label: 'Last 30 mins',
    value: '30'
  },
  {
    label: 'Last 1 hour',
    value: '60'
  },
  {
    label: 'Last 24 hours',
    value: '1440'
  },
  {
    label: 'Last 7 days',
    value: '10080'
  },
  {
    label: 'Last 30 days',
    value: '43200'
  }];
  selectedDuration: string = '';

  constructor(private splunkService: SplunkService) {
    this.services = [];
  }

  ngOnInit() {
    this.splunkService.getServices().subscribe({
      next: (data: any) => {
        console.log('Services fetched successfully:', data);
        console.log('Data type:', typeof data);
        this.services = data.services;
      },
      error: (err: any) => {
        console.error('Error fetching services:', err);
      }
    });
  }

  search() {
    console.log('Search button clicked');
    console.log('Selected Service:', this.selectedService);
    console.log('Selected Duration:', this.selectedDuration);
    let startTime = new Date(Date.now() - parseInt(this.selectedDuration) * 60000).toISOString();
    console.log('Calculated Start Time:', startTime);
    let endTime = new Date().toISOString();
    console.log('Calculated End Time:', endTime);
    this.splunkService.getErrorLogs(this.selectedService, startTime, endTime).subscribe({
      next: (data: ErrorLogsResponse) => {
        console.log('Error logs fetched successfully:', data);
        this.analysisComplete.emit(data);
      },
      error: (err: any) => {
        console.error('Error fetching error logs:', err);
      }
    });

  }
}

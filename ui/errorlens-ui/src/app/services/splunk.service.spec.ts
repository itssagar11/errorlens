import { TestBed } from '@angular/core/testing';

import { SplunkService } from './splunk.service';

describe('SplunkService', () => {
  let service: SplunkService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SplunkService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

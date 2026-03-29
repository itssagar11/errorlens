import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ErrorLensComponent } from './error-lens.component';

describe('ErrorLensComponent', () => {
  let component: ErrorLensComponent;
  let fixture: ComponentFixture<ErrorLensComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ErrorLensComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ErrorLensComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

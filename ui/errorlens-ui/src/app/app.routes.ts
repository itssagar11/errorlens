import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { DrilldownComponent } from './pages/drilldown/drilldown.component';

export const routes: Routes = [
    { path: '', component: DashboardComponent },
    { path: 'drilldown', component: DrilldownComponent },
];

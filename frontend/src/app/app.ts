import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { DashboardPage } from './dashboard-page/dashboard-page';
import { Alert } from "./utilities/alert/alert";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, DashboardPage, Alert],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
}

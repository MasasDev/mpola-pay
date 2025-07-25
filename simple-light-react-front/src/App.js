import React, { useState } from 'react';
import PaymentScheduleForm from './components/PaymentScheduleForm';
import PaymentScheduleList from './components/PaymentScheduleList';
import CustomerForm from './components/CustomerForm';
import TestFunctions from './components/TestFunctions';
import ErrorBoundary from './components/ErrorBoundary';

function App() {
  const [activeTab, setActiveTab] = useState('customers');

  return (
    <div className="container">
      <div className="header">
        <h1>Mpola Pay</h1>
        <p>Simple Payment Scheduling Made Easy</p>
      </div>

      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'customers' ? 'active' : ''}`}
          onClick={() => setActiveTab('customers')}
        >
          Create Customer
        </div>
        <div 
          className={`tab ${activeTab === 'create' ? 'active' : ''}`}
          onClick={() => setActiveTab('create')}
        >
          Create Schedule
        </div>
        <div 
          className={`tab ${activeTab === 'view' ? 'active' : ''}`}
          onClick={() => setActiveTab('view')}
        >
          View Schedules
        </div>
        <div 
          className={`tab ${activeTab === 'test' ? 'active' : ''}`}
          onClick={() => setActiveTab('test')}
        >
          🧪 Test 5-Min
        </div>
      </div>

      <ErrorBoundary>
        {activeTab === 'customers' && <CustomerForm />}
        {activeTab === 'create' && <PaymentScheduleForm />}
        {activeTab === 'view' && <PaymentScheduleList />}
        {activeTab === 'test' && <TestFunctions />}
      </ErrorBoundary>
    </div>
  );
}

export default App;

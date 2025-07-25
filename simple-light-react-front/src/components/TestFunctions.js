import React, { useState, useEffect } from 'react';
import { testAPI, paymentScheduleAPI } from '../api';
import { formatUGX, formatUGXCompact } from '../utils/currency';

const TestFunctions = () => {
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState({});
  const [schedules, setSchedules] = useState([]);
  const [selectedFrequency, setSelectedFrequency] = useState('test_5min');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(null);

  // Available test frequencies
  const frequencies = [
    { value: 'test_30sec', label: '30 Seconds (Fast Testing)' },
    { value: 'test_2min', label: '2 Minutes' },
    { value: 'test_5min', label: '5 Minutes' },
    { value: 'hourly', label: 'Hourly' },
    { value: 'daily', label: 'Daily' },
    { value: 'weekly', label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' }
  ];

  // Auto-refresh scheduled payments status
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        loadScheduledPaymentsStatus();
      }, 10000); // Refresh every 10 seconds
      setRefreshInterval(interval);
      return () => clearInterval(interval);
    } else if (refreshInterval) {
      clearInterval(refreshInterval);
      setRefreshInterval(null);
    }
  }, [autoRefresh, refreshInterval]);

  const handleApiCall = async (apiFunction, resultKey, ...args) => {
    setLoading(true);
    try {
      const response = await apiFunction(...args);
      setResults(prev => ({
        ...prev,
        [resultKey]: {
          success: true,
          data: response.data,
          timestamp: new Date().toLocaleTimeString()
        }
      }));
    } catch (error) {
      setResults(prev => ({
        ...prev,
        [resultKey]: {
          success: false,
          error: error.response?.data || error.message,
          timestamp: new Date().toLocaleTimeString()
        }
      }));
    }
    setLoading(false);
  };

  const loadScheduledPaymentsStatus = async () => {
    try {
      const response = await testAPI.getScheduledPaymentsStatus();
      setSchedules(response.data.schedules || []);
    } catch (error) {
      console.error('Failed to load scheduled payments status:', error);
    }
  };

  const loadSchedules = async () => {
    try {
      const response = await paymentScheduleAPI.getSchedules();
      setSchedules(response.data.payment_schedules || []);
    } catch (error) {
      console.error('Failed to load schedules:', error);
    }
  };

  // Load initial data
  useEffect(() => {
    loadSchedules();
    loadScheduledPaymentsStatus();
  }, []);

  const ResultDisplay = ({ result, title }) => {
    if (!result) return null;

    // Helper function to format JSON with UGX amounts
    const formatResultData = (data) => {
      if (typeof data === 'object' && data !== null) {
        const formatted = { ...data };
        
        // Format common amount fields
        const amountFields = ['amount', 'total_amount', 'subtotal_amount', 'processing_fee', 'total_funded_amount', 'total_payments_made'];
        amountFields.forEach(field => {
          if (formatted[field] !== undefined && formatted[field] !== null) {
            formatted[`${field}_formatted`] = formatUGX(formatted[field]);
          }
        });

        // Format nested schedules if present
        if (formatted.schedules && Array.isArray(formatted.schedules)) {
          formatted.schedules = formatted.schedules.map(schedule => ({
            ...schedule,
            ...(schedule.total_amount && { total_amount_formatted: formatUGX(schedule.total_amount) }),
            ...(schedule.amount && { amount_formatted: formatUGX(schedule.amount) })
          }));
        }

        return formatted;
      }
      return data;
    };

    const displayData = result.success ? formatResultData(result.data) : result.error;

    return (
      <div className={`result-card ${result.success ? 'success' : 'error'}`}>
        <div className="result-header">
          <h4>{title.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</h4>
          <span className="result-timestamp">{result.timestamp}</span>
        </div>
        <div className="result-content">
          <pre>{JSON.stringify(displayData, null, 2)}</pre>
        </div>
      </div>
    );
  };

  return (
    <div className="test-functions">
      <div className="test-header">
        <h2>🧪 Test Functions</h2>
        <p>Test the 5-minute payment scheduling and Bitnob API integration with UGX payments</p>
        <div className="header-stats">
          <div className="stat-badge">
            <span className="stat-icon">🏦</span>
            <span>UGX Payments</span>
          </div>
          <div className="stat-badge">
            <span className="stat-icon">⚡</span>
            <span>Real-time Testing</span>
          </div>
          <div className="stat-badge">
            <span className="stat-icon">🔄</span>
            <span>Auto-refresh</span>
          </div>
        </div>
      </div>

      <div className="test-grid">
        {/* Quick Test Actions */}
        <div className="test-section">
          <h3>🚀 Quick Test Actions</h3>
          
          <div className="test-action">
            <button 
              onClick={() => handleApiCall(testAPI.create5MinTest, 'create5MinTest')}
              disabled={loading}
              className="btn btn-primary"
            >
              Create 5-Min Test Payment 💰
            </button>
            <p className="test-description">
              Creates a complete test payment schedule with 5-minute intervals and immediately triggers a Bitnob API payment in UGX
            </p>
          </div>

          <div className="test-action">
            <button 
              onClick={() => handleApiCall(testAPI.checkBitnobApiStatus, 'bitnobStatus')}
              disabled={loading}
              className="btn btn-secondary"
            >
              Check Bitnob API Status 🔍
            </button>
            <p className="test-description">
              Verify connection to Bitnob API and check service availability for UGX transactions
            </p>
          </div>
        </div>

        {/* Test Schedule Creation */}
        <div className="test-section">
          <h3>📅 Create Test Schedule</h3>
          
          <div className="frequency-selector">
            <label htmlFor="frequency">Select Frequency:</label>
            <select 
              id="frequency"
              value={selectedFrequency} 
              onChange={(e) => setSelectedFrequency(e.target.value)}
            >
              {frequencies.map(freq => (
                <option key={freq.value} value={freq.value}>
                  {freq.label}
                </option>
              ))}
            </select>
          </div>

          <button 
            onClick={() => handleApiCall(testAPI.createTestSchedule, 'createTestSchedule', selectedFrequency)}
            disabled={loading}
            className="btn btn-primary"
          >
            Create Test Schedule ({selectedFrequency})
          </button>
        </div>

        {/* Payment Processing */}
        <div className="test-section">
          <h3>⚡ Payment Processing</h3>
          
          <div className="test-action">
            <button 
              onClick={() => handleApiCall(testAPI.triggerScheduledPayments, 'triggerPayments')}
              disabled={loading}
              className="btn btn-warning"
            >
              Trigger All Scheduled Payments ⚡
            </button>
            <p className="test-description">
              Manually process all due UGX payments across all active schedules
            </p>
          </div>

          <div className="auto-refresh-toggle">
            <label>
              <input 
                type="checkbox" 
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
              />
              Auto-refresh status (every 10s)
            </label>
          </div>

          <button 
            onClick={loadScheduledPaymentsStatus}
            disabled={loading}
            className="btn btn-secondary"
          >
            Refresh Payment Status
          </button>
        </div>
      </div>

      {/* Active Test Schedules */}
      {schedules.length > 0 && (
        <div className="active-schedules">
          <h3>📊 Active Test Schedules</h3>
          <div className="schedules-grid">
            {schedules.map(schedule => (
              <div key={schedule.schedule_id} className="schedule-card">
                <div className="schedule-header">
                  <h4>{schedule.title}</h4>
                  <div className="schedule-status">
                    <span className={`status-badge ${schedule.status || 'active'}`}>
                      {(schedule.status || 'active').toUpperCase()}
                    </span>
                  </div>
                </div>
                
                <div className="schedule-info">
                  <div className="info-row">
                    <span className="info-label">💰 Total Amount:</span>
                    <span className="info-value amount-value">
                      {formatUGX(schedule.total_amount || schedule.amount || 0)}
                    </span>
                  </div>
                  
                  <div className="info-row">
                    <span className="info-label">📅 Frequency:</span>
                    <span className="info-value">{schedule.frequency}</span>
                  </div>
                  
                  <div className="info-row">
                    <span className="info-label">⏰ Next Payment:</span>
                    <span className="info-value">
                      {schedule.next_payment_date 
                        ? new Date(schedule.next_payment_date).toLocaleString()
                        : 'Not scheduled'
                      }
                    </span>
                  </div>
                  
                  <div className="info-row">
                    <span className="info-label">🚨 Payment Due:</span>
                    <span className={`info-value ${schedule.is_payment_due ? 'status-due' : 'status-waiting'}`}>
                      {schedule.is_payment_due ? '🔴 YES - Ready to Process' : '🟢 No - Waiting'}
                    </span>
                  </div>
                  
                  <div className="progress-section">
                    <div className="progress-header">
                      <span className="info-label">📈 Progress:</span>
                      <span className="progress-percentage">{schedule.completion_percentage || 0}%</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${schedule.completion_percentage || 0}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="transactions-summary">
                    <div className="transaction-stats">
                      <div className="stat-item success">
                        <span className="stat-icon">✅</span>
                        <span className="stat-count">{schedule.successful_transactions || 0}</span>
                        <span className="stat-label">Success</span>
                      </div>
                      <div className="stat-item pending">
                        <span className="stat-icon">⏳</span>
                        <span className="stat-count">{schedule.pending_transactions || 0}</span>
                        <span className="stat-label">Pending</span>
                      </div>
                      <div className="stat-item failed">
                        <span className="stat-icon">❌</span>
                        <span className="stat-count">{schedule.failed_transactions || 0}</span>
                        <span className="stat-label">Failed</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div className="schedule-actions">
                  <button 
                    onClick={() => handleApiCall(testAPI.triggerScheduledPayments, `triggerSchedule_${schedule.schedule_id}`, schedule.schedule_id)}
                    disabled={loading || !schedule.is_payment_due}
                    className={`btn btn-sm ${schedule.is_payment_due ? 'btn-primary' : 'btn-secondary'}`}
                  >
                    {schedule.is_payment_due ? '🚀 Process Payment Now' : '⏸️ Not Due Yet'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Results Display */}
      <div className="results-section">
        <h3>📋 Test Results</h3>
        {Object.entries(results).map(([key, result]) => (
          <ResultDisplay key={key} result={result} title={key} />
        ))}
      </div>

      {/* Help Section */}
      <div className="help-section">
        <h3>❓ How to Test 5-Minute UGX Payments</h3>
        <ol>
          <li><strong>Quick Test:</strong> Click "Create 5-Min Test Payment" to create a complete test setup with UGX amounts</li>
          <li><strong>Manual Test:</strong> Create a test schedule with your preferred frequency using UGX currency</li>
          <li><strong>Monitor:</strong> Enable auto-refresh to watch UGX payments process in real-time</li>
          <li><strong>Trigger:</strong> Use "Trigger Scheduled Payments" to manually process due UGX payments</li>
          <li><strong>Verify:</strong> Check Bitnob API status to ensure external service connectivity for UGX transactions</li>
        </ol>
        
        <div className="test-tips">
          <h4>💡 UGX Testing Tips</h4>
          <ul>
            <li>All amounts are displayed in <strong>UGX (Ugandan Shillings)</strong> with proper formatting</li>
            <li>Use "test_30sec" frequency for fastest testing of UGX payments</li>
            <li>Monitor the console for detailed API logs including UGX transaction details</li>
            <li>Check that schedules show "🔴 YES" when UGX payments are due</li>
            <li>Successful UGX payments will show in the progress counter with formatted amounts</li>
            <li>Processing fees are calculated as a percentage of the UGX subtotal</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TestFunctions;

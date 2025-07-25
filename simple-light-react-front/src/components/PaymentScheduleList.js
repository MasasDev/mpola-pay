import React, { useState, useEffect } from 'react';
import { paymentScheduleAPI } from '../api';

const PaymentScheduleList = () => {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      const response = await paymentScheduleAPI.getSchedules();
      // Backend returns { payment_schedules: [...], count: N }
      setSchedules(response.data.payment_schedules || []);
      setError('');
    } catch (error) {
      // Extract error message from response
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail || 
                          error.response?.data ||
                          error.message ||
                          'Failed to fetch payment schedules';
      setError(errorMessage);
      console.error('Error fetching schedules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFundSchedule = async (scheduleId) => {
    const schedule = schedules.find(s => s.id === scheduleId);
    if (!schedule) {
      alert('Schedule not found');
      return;
    }

    if (schedule.is_adequately_funded) {
      alert('This schedule is already adequately funded');
      return;
    }

    // Let user choose network
    const networks = ['TRON', 'ETHEREUM', 'BSC', 'POLYGON'];
    const networkChoice = prompt(
      `Choose network for USDT deposit:\n\n` +
      `1. TRON (TRC20) - Recommended (low fees)\n` +
      `2. ETHEREUM (ERC20)\n` +
      `3. BSC (BEP20)\n` +
      `4. POLYGON (MATIC)\n\n` +
      `Enter 1, 2, 3, or 4 (or press Cancel to abort):`
    );

    if (!networkChoice) return; // User cancelled

    const networkIndex = parseInt(networkChoice) - 1;
    if (networkIndex < 0 || networkIndex >= networks.length) {
      alert('Invalid network choice. Please select 1, 2, 3, or 4.');
      return;
    }

    const selectedNetwork = networks[networkIndex];

    const confirmed = window.confirm(
      `Generate ${selectedNetwork} USDT deposit address for funding schedule "${schedule.title}"?\n\n` +
      `Remaining amount needed: ${formatCurrency(schedule.funding_shortfall)}`
    );

    if (confirmed) {
      try {
        const response = await paymentScheduleAPI.fundSchedule(scheduleId, selectedNetwork);
        const data = response.data;
        
        // Show funding instructions to user
        const instructions = `
FUNDING INSTRUCTIONS:

Network: ${data.funding_details.network}
Amount: ${data.funding_details.usdt_required} USDT
Deposit Address: ${data.funding_details.deposit_address}

${data.instructions.step_1}
${data.instructions.step_2}
${data.instructions.step_3}
${data.instructions.step_4}

Reference: ${data.funding_details.reference}

⚠️ IMPORTANT: Make sure to use the correct network (${data.funding_details.network}) when sending USDT!
        `;
        
        alert(instructions);
        fetchSchedules(); // Refresh the list
      } catch (error) {
        console.error('Funding error:', error);
        
        // Handle different types of errors
        if (error.response?.status === 400) {
          const errorData = error.response.data;
          
          if (errorData.error?.includes('already adequately funded')) {
            alert(`Schedule is already fully funded!\n\nRequired: ${errorData.funding_details?.required}\nFunded: ${errorData.funding_details?.funded}`);
          } else if (errorData.error?.includes('pending fund transaction')) {
            const existing = errorData.existing_transaction;
            alert(`A funding transaction is already pending:\n\nReference: ${existing.reference}\nAmount: ${existing.usdt_required} USDT\nDeposit Address: ${existing.deposit_address}\nNetwork: ${existing.network}\n\nPlease complete the existing transaction or wait for it to expire.`);
          } else {
            alert(`Error: ${errorData.error || 'Failed to generate funding address'}`);
          }
        } else {
          const errorMessage = error.response?.data?.error || 
                              error.response?.data?.message || 
                              error.message ||
                              'Failed to generate funding address';
          alert(`Error: ${errorMessage}`);
        }
      }
    }
  };

  const handleToggleSchedule = async (scheduleId, currentStatus) => {
    const action = currentStatus === 'active' ? 'pause' : 'activate';
    try {
      await paymentScheduleAPI.toggleSchedule(scheduleId, action);
      fetchSchedules(); // Refresh the list
    } catch (error) {
      alert(`Failed to ${action} schedule`);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount || 0);
  };

  if (loading) {
    return <div className="loading">Loading payment schedules...</div>;
  }

  if (error) {
    // Handle both string errors and error objects
    const errorMessage = typeof error === 'string' 
      ? error 
      : error.message || error.detail || JSON.stringify(error);
    return <div className="error">{errorMessage}</div>;
  }

  return (
    <div className="card">
      <h2>Payment Schedules</h2>
      
      {schedules.length === 0 ? (
        <p>No payment schedules found. Create your first schedule!</p>
      ) : (
        <div className="schedule-list">
          {schedules.map((schedule) => (
            <div key={schedule.id} className="schedule-item">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <h3 style={{ margin: '0 0 0.5rem 0' }}>{schedule.title}</h3>
                  <span className={`schedule-status status-${schedule.status}`}>
                    {schedule.status}
                  </span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div><strong>Total: {formatCurrency(schedule.total_amount)}</strong></div>
                  <div>Funded: {formatCurrency(schedule.total_funded_amount)}</div>
                </div>
              </div>

              {schedule.description && (
                <p style={{ margin: '0.5rem 0', color: '#666' }}>{schedule.description}</p>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', margin: '1rem 0' }}>
                <div>
                  <strong>Customer:</strong> {schedule.customer_email}
                </div>
                <div>
                  <strong>Frequency:</strong> {schedule.frequency}
                </div>
                <div>
                  <strong>Start Date:</strong> {formatDate(schedule.start_date)}
                </div>
                <div>
                  <strong>Next Payment:</strong> {formatDate(schedule.next_payment_date)}
                </div>
              </div>

              <div style={{ margin: '1rem 0' }}>
                <strong>Funding Status:</strong>
                <div style={{ background: '#f8f9fa', padding: '0.5rem', borderRadius: '4px', marginTop: '0.5rem' }}>
                  <div>Available Balance: {formatCurrency(schedule.available_balance)}</div>
                  <div>Total Payments Made: {formatCurrency(schedule.total_payments_made)}</div>
                  {schedule.funding_shortfall > 0 && (
                    <div style={{ color: '#dc3545' }}>
                      Shortfall: {formatCurrency(schedule.funding_shortfall)}
                    </div>
                  )}
                  <div>
                    Adequately Funded: {schedule.is_adequately_funded ? '✅ Yes' : '❌ No'}
                  </div>
                </div>
              </div>

              {schedule.receivers && schedule.receivers.length > 0 && (
                <div style={{ margin: '1rem 0' }}>
                  <strong>Recipients ({schedule.receivers.length}):</strong>
                  <div style={{ marginTop: '0.5rem' }}>
                    {schedule.receivers.map((receiver, index) => (
                      <div key={receiver.id || index} style={{ 
                        background: '#f8f9fa', 
                        padding: '0.5rem', 
                        borderRadius: '4px', 
                        marginBottom: '0.5rem' 
                      }}>
                        <div><strong>{receiver.name}</strong> ({receiver.country_code}{receiver.phone})</div>
                        <div>
                          {formatCurrency(receiver.amount_per_installment)} × {receiver.number_of_installments} installments 
                          = {formatCurrency(receiver.total_amount)}
                        </div>
                        <div>
                          Progress: {receiver.completed_installments}/{receiver.number_of_installments} 
                          ({receiver.progress_percentage}%)
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                <button
                  className="btn"
                  onClick={() => handleFundSchedule(schedule.id)}
                  disabled={schedule.status === 'completed' || schedule.is_adequately_funded}
                  title={schedule.is_adequately_funded ? 'Schedule is already adequately funded' : 'Generate USDT deposit address for funding'}
                >
                  {schedule.is_adequately_funded ? 'Fully Funded' : 'Fund Schedule'}
                </button>
                
                {schedule.status !== 'completed' && (
                  <button
                    className="btn"
                    onClick={() => handleToggleSchedule(schedule.id, schedule.status)}
                    style={{ 
                      background: schedule.status === 'active' ? '#ffc107' : '#28a745'
                    }}
                  >
                    {schedule.status === 'active' ? 'Pause' : 'Activate'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      
      <button 
        className="btn" 
        onClick={fetchSchedules}
        style={{ marginTop: '1rem' }}
      >
        Refresh
      </button>
    </div>
  );
};

export default PaymentScheduleList;

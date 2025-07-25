import React, { useState } from 'react';
import { paymentScheduleAPI } from '../api';

const PaymentScheduleForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    title: '',
    description: '',
    frequency: 'monthly',
    start_date: '',
  });

  const [receivers, setReceivers] = useState([
    {
      name: '',
      phone: '',
      countryCode: '+234',
      amountPerInstallment: '',
      numberOfInstallments: '',
    }
  ]);

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleReceiverChange = (index, field, value) => {
    const updatedReceivers = receivers.map((receiver, i) => 
      i === index ? { ...receiver, [field]: value } : receiver
    );
    setReceivers(updatedReceivers);
  };

  const addReceiver = () => {
    setReceivers([...receivers, {
      name: '',
      phone: '',
      countryCode: '+234',
      amountPerInstallment: '',
      numberOfInstallments: '',
    }]);
  };

  const removeReceiver = (index) => {
    if (receivers.length > 1) {
      setReceivers(receivers.filter((_, i) => i !== index));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const scheduleData = {
        ...formData,
        start_date: new Date(formData.start_date).toISOString(),
        receivers: receivers.map(receiver => ({
          ...receiver,
          amountPerInstallment: parseFloat(receiver.amountPerInstallment),
          numberOfInstallments: parseInt(receiver.numberOfInstallments),
        }))
      };

      await paymentScheduleAPI.createSchedule(scheduleData);
      
      setMessage({ 
        type: 'success', 
        text: 'Payment schedule created successfully!' 
      });
      
      // Reset form
      setFormData({
        email: '',
        title: '',
        description: '',
        frequency: 'monthly',
        start_date: '',
      });
      
      setReceivers([{
        name: '',
        phone: '',
        countryCode: '+234',
        amountPerInstallment: '',
        numberOfInstallments: '',
      }]);

    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Failed to create payment schedule' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Create Payment Schedule</h2>
      
      {message.text && (
        <div className={message.type === 'error' ? 'error' : 'success'}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Customer Email:</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="title">Schedule Title:</label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="description">Description:</label>
          <textarea
            id="description"
            name="description"
            value={formData.description}
            onChange={handleInputChange}
            rows="3"
          />
        </div>

        <div className="form-group">
          <label htmlFor="frequency">Payment Frequency:</label>
          <select
            id="frequency"
            name="frequency"
            value={formData.frequency}
            onChange={handleInputChange}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="test_30sec">Test (30 seconds)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="start_date">Start Date:</label>
          <input
            type="datetime-local"
            id="start_date"
            name="start_date"
            value={formData.start_date}
            onChange={handleInputChange}
            required
          />
        </div>

        <h3>Recipients</h3>
        {receivers.map((receiver, index) => (
          <div key={index} className="receiver-item">
            <div className="receiver-header">
              <h4>Recipient {index + 1}</h4>
              {receivers.length > 1 && (
                <button
                  type="button"
                  className="btn-remove"
                  onClick={() => removeReceiver(index)}
                >
                  Remove
                </button>
              )}
            </div>

            <div className="form-group">
              <label htmlFor={`name-${index}`}>Name:</label>
              <input
                type="text"
                id={`name-${index}`}
                value={receiver.name}
                onChange={(e) => handleReceiverChange(index, 'name', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor={`countryCode-${index}`}>Country Code:</label>
              <select
                id={`countryCode-${index}`}
                value={receiver.countryCode}
                onChange={(e) => handleReceiverChange(index, 'countryCode', e.target.value)}
              >
                <option value="+234">+234 (Nigeria)</option>
                <option value="+254">+254 (Kenya)</option>
                <option value="+256">+256 (Uganda)</option>
                <option value="+27">+27 (South Africa)</option>
                <option value="+233">+233 (Ghana)</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor={`phone-${index}`}>Phone Number:</label>
              <input
                type="tel"
                id={`phone-${index}`}
                value={receiver.phone}
                onChange={(e) => handleReceiverChange(index, 'phone', e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor={`amount-${index}`}>Amount per Installment:</label>
              <input
                type="number"
                id={`amount-${index}`}
                value={receiver.amountPerInstallment}
                onChange={(e) => handleReceiverChange(index, 'amountPerInstallment', e.target.value)}
                min="0"
                step="0.01"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor={`installments-${index}`}>Number of Installments:</label>
              <input
                type="number"
                id={`installments-${index}`}
                value={receiver.numberOfInstallments}
                onChange={(e) => handleReceiverChange(index, 'numberOfInstallments', e.target.value)}
                min="1"
                required
              />
            </div>
          </div>
        ))}

        <button type="button" className="btn-add" onClick={addReceiver}>
          Add Another Recipient
        </button>

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Creating...' : 'Create Payment Schedule'}
        </button>
      </form>
    </div>
  );
};

export default PaymentScheduleForm;

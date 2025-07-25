import React, { useState } from 'react';
import { customerAPI } from '../api';

const CustomerForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    firstName: '',
    lastName: '',
    phone: '',
    countryCode: '+234',
  });

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await customerAPI.createCustomer(formData);
      
      setMessage({ 
        type: 'success', 
        text: `Customer created successfully! Bitnob ID: ${response.data.bitnob_id}` 
      });
      
      // Reset form
      setFormData({
        email: '',
        firstName: '',
        lastName: '',
        phone: '',
        countryCode: '+234',
      });

    } catch (error) {
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.detail || 
                          'Failed to create customer';
      
      setMessage({ 
        type: 'error', 
        text: errorMessage
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Create Customer</h2>
      <p style={{ color: '#666', marginBottom: '2rem' }}>
        Create a new customer account in the system. This customer can then be used for payment schedules.
      </p>
      
      {message.text && (
        <div className={message.type === 'error' ? 'error' : 'success'}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email Address:</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            placeholder="customer@example.com"
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div className="form-group">
            <label htmlFor="firstName">First Name:</label>
            <input
              type="text"
              id="firstName"
              name="firstName"
              value={formData.firstName}
              onChange={handleInputChange}
              required
              placeholder="John"
            />
          </div>

          <div className="form-group">
            <label htmlFor="lastName">Last Name:</label>
            <input
              type="text"
              id="lastName"
              name="lastName"
              value={formData.lastName}
              onChange={handleInputChange}
              required
              placeholder="Doe"
            />
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="countryCode">Country Code:</label>
          <select
            id="countryCode"
            name="countryCode"
            value={formData.countryCode}
            onChange={handleInputChange}
            required
          >
            <option value="+234">+234 (Nigeria)</option>
            <option value="+254">+254 (Kenya)</option>
            <option value="+256">+256 (Uganda)</option>
            <option value="+27">+27 (South Africa)</option>
            <option value="+233">+233 (Ghana)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="phone">Phone Number:</label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            required
            placeholder="1234567890"
          />
          <small style={{ color: '#666', fontSize: '0.875rem' }}>
            Enter phone number without country code or special characters
          </small>
        </div>

        <button type="submit" className="btn" disabled={loading}>
          {loading ? 'Creating Customer...' : 'Create Customer'}
        </button>
      </form>

      <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8f9fa', borderRadius: '4px' }}>
        <h4 style={{ margin: '0 0 0.5rem 0', color: '#333' }}>What happens next?</h4>
        <ul style={{ margin: 0, paddingLeft: '1.5rem', color: '#666' }}>
          <li>Customer account is created in the Bitnob system</li>
          <li>You'll receive a unique Bitnob ID for this customer</li>
          <li>Customer can now be used in payment schedules</li>
          <li>If customer already exists, you'll get their existing Bitnob ID</li>
        </ul>
      </div>
    </div>
  );
};

export default CustomerForm;

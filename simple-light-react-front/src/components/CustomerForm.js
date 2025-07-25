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
      console.error('Customer creation error:', error);
      
      let errorMessage = 'Failed to create customer. Please try again.';
      
      if (error.response?.data) {
        const errorData = error.response.data;
        
        // Try multiple possible error message fields
        errorMessage = errorData.message || 
                      errorData.error || 
                      errorData.detail || 
                      errorData.non_field_errors?.[0] ||
                      errorMessage;
        
        // Handle specific error cases
        if (errorData.provider_error) {
          errorMessage += ` (Provider: ${errorData.provider_error.message || 'Unknown provider error'})`;
        }
      } else if (error.message) {
        errorMessage = `Network error: ${error.message}`;
      }
      
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
          {message.type === 'error' && '⚠️ '}
          {message.type === 'success' && '✅ '}
          {message.text}
          
          {/* Add helpful tips for common errors */}
          {message.type === 'error' && message.text.toLowerCase().includes('connect') && (
            <div style={{ 
              marginTop: '0.5rem', 
              fontSize: '0.875rem', 
              color: '#666',
              padding: '0.5rem',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px'
            }}>
              💡 <strong>Troubleshooting Tips:</strong>
              <ul style={{ margin: '0.5rem 0 0 0', paddingLeft: '1.5rem' }}>
                <li>Check your internet connection</li>
                <li>Verify the backend server is running</li>
                <li>Contact support if the problem persists</li>
              </ul>
            </div>
          )}
          
          {message.type === 'error' && message.text.toLowerCase().includes('provider') && (
            <div style={{ 
              marginTop: '0.5rem', 
              fontSize: '0.875rem', 
              color: '#666',
              padding: '0.5rem',
              backgroundColor: '#f8f9fa',
              borderRadius: '4px'
            }}>
              💡 This is likely a temporary issue with our payment provider. Please try again in a few minutes.
            </div>
          )}
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

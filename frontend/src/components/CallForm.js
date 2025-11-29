import React, { useState } from 'react';
import api from '../api/axios';
import './CallForm.css';

function CallForm({ onCallCreated }) {
  const [formData, setFormData] = useState({
    phone_number: '',
    customer_name: '',
    purpose: 'schedule_appointment',
    preferred_date: '',
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await api.post('/calls/', formData);
      setMessage({
        type: 'success',
        text: `Call initiated successfully! Call ID: ${response.data.call.id}`
      });
      
      // Reset form
      setFormData({
        phone_number: '',
        customer_name: '',
        purpose: 'schedule_appointment',
        preferred_date: '',
        notes: ''
      });

      // Notify parent
      if (onCallCreated) {
        onCallCreated();
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to initiate call'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="call-form">
      <h2>Initiate AI Call</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="phone_number">Phone Number *</label>
          <input
            type="tel"
            id="phone_number"
            name="phone_number"
            value={formData.phone_number}
            onChange={handleChange}
            placeholder="+48 123 456 789"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="customer_name">Customer Name</label>
          <input
            type="text"
            id="customer_name"
            name="customer_name"
            value={formData.customer_name}
            onChange={handleChange}
            placeholder="Jan Kowalski"
          />
        </div>

        <div className="form-group">
          <label htmlFor="purpose">Call Purpose *</label>
          <input
            type="text"
            id="purpose"
            name="purpose"
            value={formData.purpose}
            onChange={handleChange}
            placeholder="Schedule appointment"
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="preferred_date">Preferred Date</label>
          <input
            type="date"
            id="preferred_date"
            name="preferred_date"
            value={formData.preferred_date}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="notes">Additional Notes</label>
          <textarea
            id="notes"
            name="notes"
            value={formData.notes}
            onChange={handleChange}
            placeholder="Any additional information..."
            rows="4"
          />
        </div>

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? '📞 Initiating Call...' : '📞 Start Call'}
        </button>
      </form>
    </div>
  );
}

export default CallForm;


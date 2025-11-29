import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import './CallsList.css';

function CallsList() {
  const [calls, setCalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCalls();
  }, []);

  const fetchCalls = async () => {
    try {
      const response = await api.get('/calls/');
      setCalls(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch calls');
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    const statusMap = {
      pending: 'status-pending',
      in_progress: 'status-progress',
      completed: 'status-completed',
      failed: 'status-failed'
    };
    return statusMap[status] || 'status-pending';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pl-PL');
  };

  if (loading) {
    return <div className="loading">Loading calls...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (calls.length === 0) {
    return (
      <div className="empty-state">
        <p>No calls yet. Start by creating a new call!</p>
      </div>
    );
  }

  return (
    <div className="calls-list">
      <h2>Calls History</h2>
      <div className="calls-grid">
        {calls.map((call) => (
          <div key={call.id} className="call-card">
            <div className="call-header">
              <span className={`status-badge ${getStatusBadgeClass(call.status)}`}>
                {call.status.replace('_', ' ')}
              </span>
              <span className="call-id">ID: {call.id.slice(0, 8)}...</span>
            </div>
            
            <div className="call-body">
              <div className="call-info">
                <strong>📞 Phone:</strong> {call.phone_number}
              </div>
              {call.customer_name && (
                <div className="call-info">
                  <strong>👤 Name:</strong> {call.customer_name}
                </div>
              )}
              <div className="call-info">
                <strong>🎯 Purpose:</strong> {call.purpose}
              </div>
              <div className="call-info">
                <strong>🕐 Created:</strong> {formatDate(call.created_at)}
              </div>
              {call.transcript && (
                <div className="call-transcript">
                  <strong>📝 Transcript:</strong>
                  <p>{call.transcript}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default CallsList;


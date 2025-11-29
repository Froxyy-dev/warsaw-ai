import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import './AppointmentsList.css';

function AppointmentsList() {
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAppointments();
  }, []);

  const fetchAppointments = async () => {
    try {
      const response = await api.get('/appointments/');
      setAppointments(response.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch appointments');
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    const statusMap = {
      scheduled: 'status-scheduled',
      confirmed: 'status-confirmed',
      cancelled: 'status-cancelled',
      completed: 'status-completed'
    };
    return statusMap[status] || 'status-scheduled';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pl-PL');
  };

  if (loading) {
    return <div className="loading">Loading appointments...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (appointments.length === 0) {
    return (
      <div className="empty-state">
        <p>No appointments yet. Complete calls to create appointments!</p>
      </div>
    );
  }

  return (
    <div className="appointments-list">
      <h2>Scheduled Appointments</h2>
      <div className="appointments-grid">
        {appointments.map((appointment) => (
          <div key={appointment.id} className="appointment-card">
            <div className="appointment-header">
              <span className={`status-badge ${getStatusBadgeClass(appointment.status)}`}>
                {appointment.status}
              </span>
              <span className="appointment-id">ID: {appointment.id.slice(0, 8)}...</span>
            </div>
            
            <div className="appointment-body">
              <div className="appointment-info">
                <strong>👤 Customer:</strong> {appointment.customer_name}
              </div>
              <div className="appointment-info">
                <strong>📞 Phone:</strong> {appointment.phone_number}
              </div>
              <div className="appointment-info">
                <strong>📅 Scheduled:</strong> {appointment.scheduled_date}
              </div>
              <div className="appointment-info">
                <strong>🕐 Created:</strong> {formatDate(appointment.created_at)}
              </div>
              {appointment.notes && (
                <div className="appointment-notes">
                  <strong>📝 Notes:</strong>
                  <p>{appointment.notes}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default AppointmentsList;


import React, { useState } from 'react';
import './App.css';
import CallForm from './components/CallForm';
import CallsList from './components/CallsList';
import AppointmentsList from './components/AppointmentsList';

function App() {
  const [activeTab, setActiveTab] = useState('new-call');
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleCallCreated = () => {
    setRefreshTrigger(prev => prev + 1);
    setActiveTab('calls');
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 AI Call Agent</h1>
        <p>Schedule appointments with AI-powered calls</p>
      </header>

      <div className="container">
        <nav className="tabs">
          <button 
            className={activeTab === 'new-call' ? 'active' : ''}
            onClick={() => setActiveTab('new-call')}
          >
            📞 New Call
          </button>
          <button 
            className={activeTab === 'calls' ? 'active' : ''}
            onClick={() => setActiveTab('calls')}
          >
            📋 Calls History
          </button>
          <button 
            className={activeTab === 'appointments' ? 'active' : ''}
            onClick={() => setActiveTab('appointments')}
          >
            📅 Appointments
          </button>
        </nav>

        <div className="tab-content">
          {activeTab === 'new-call' && <CallForm onCallCreated={handleCallCreated} />}
          {activeTab === 'calls' && <CallsList key={refreshTrigger} />}
          {activeTab === 'appointments' && <AppointmentsList key={refreshTrigger} />}
        </div>
      </div>
    </div>
  );
}

export default App;


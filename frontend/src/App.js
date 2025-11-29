import React from 'react';
import './App.css';
import ChatWindow from './components/ChatWindow';

function App() {
  return (
    <div className="App">
      <div className="app-container">
        <div className="app-header">
          <div className="logo">💬</div>
          <h1>AI Chat</h1>
        </div>
        <ChatWindow />
      </div>
    </div>
  );
}

export default App;

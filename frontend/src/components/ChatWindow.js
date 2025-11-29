import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import {
  sendMessage as sendMessageApi,
  createConversation,
  getConversations,
  getConversation,
  transcribeAudio,
} from "../api/chatApi";

function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);
  const [isSearching, setIsSearching] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const initialized = useRef(false);
  const autoRefreshInterval = useRef(null);

  // Initialize - load existing conversation or prepare for new one
  useEffect(() => {
    if (initialized.current) return;
    initialized.current = true;

    const init = async () => {
      try {
        const conversations = await getConversations();
        if (conversations.length > 0) {
          // Load most recent conversation
          const conv = await getConversation(conversations[0].id);
          setConversationId(conv.id);
          setMessages(conv.messages || []);
        }
      } catch (err) {
        console.error("Failed to load conversation:", err);
      }
    };

    init();
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Auto-refresh conversation when searching
  useEffect(() => {
    if (isSearching && conversationId) {
      console.log("🔄 Starting auto-refresh (searching venues/bakeries)...");

      autoRefreshInterval.current = setInterval(async () => {
        try {
          console.log("🔄 Auto-refreshing conversation...");
          const conv = await getConversation(conversationId);
          setMessages(conv.messages);

          // Check if we're still searching by looking at last message
          const lastMsg = conv.messages[conv.messages.length - 1];
          if (
            lastMsg &&
            (lastMsg.content.includes("🎉 Wszystko gotowe") ||
              lastMsg.content.includes("🎉 Zakończono wszystkie zadania"))
          ) {
            console.log("✅ Process complete, stopping auto-refresh");
            setIsSearching(false);
          }
        } catch (err) {
          console.error("Auto-refresh failed:", err);
        }
      }, 2000); // Refresh every 2 seconds

      return () => {
        if (autoRefreshInterval.current) {
          console.log("⏹️ Stopping auto-refresh");
          clearInterval(autoRefreshInterval.current);
        }
      };
    }
  }, [isSearching, conversationId]);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const ensureConversation = async () => {
    if (conversationId) return conversationId;

    // Create new conversation
    const response = await createConversation();
    const newId = response.conversation.id;
    setConversationId(newId);
    return newId;
  };

  const handleSendMessage = async (messageContent, isVoiceMessage = false) => {
    if (!messageContent.trim() || isLoading) {
      return;
    }

    if (!isVoiceMessage) {
      setInputValue(""); // Clear input only if it's a text message
    }
    setError(null);

    // Optimistic update - add user message immediately
    const userMessage = {
      id: `temp-${Date.now()}`,
      role: "user",
      content: messageContent,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Ensure conversation exists
      const convId = await ensureConversation();

      // Send message to backend
      const response = await sendMessageApi(convId, messageContent);

      // Reload entire conversation from backend
      const updatedConv = await getConversation(convId);
      setMessages(updatedConv.messages || []);

      // No speech synthesis, so just update messages
      // Check if backend is processing - if so, start auto-refresh
      const lastMessage = updatedConv.messages[updatedConv.messages.length - 1];
      if (
        lastMessage &&
        (lastMessage.content.includes("🔍 Zaczynam wyszukiwanie") ||
          lastMessage.content.includes("📞 Rozpoczynam wykonywanie"))
      ) {
        console.log("🔍 Detected active processing, enabling auto-refresh");
        setIsSearching(true);
      }
    } catch (err) {
      console.error("Failed to send message:", err);
      setError(
        `Błąd: ${
          err.response?.data?.detail ||
          err.message ||
          "Nie udało się wysłać wiadomości"
        }`
      );
      // Remove optimistic user message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
      // Restore input value only if it was a text message and it failed
      if (!isVoiceMessage) {
        setInputValue(messageContent);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleFormSubmit = (e) => {
    e.preventDefault();
    handleSendMessage(inputValue, false); // Explicitly mark as text message
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputValue, false); // Explicitly mark as text message
    }
  };

  const handleRecord = async () => {
    if (isRecording) {
      // Stop recording
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerIntervalRef.current);
    } else {
      // Start recording
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: true,
        });
        mediaRecorderRef.current = new MediaRecorder(stream);
        mediaRecorderRef.current.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };
        mediaRecorderRef.current.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, {
            type: "audio/webm",
          });
          audioChunksRef.current = [];
          try {
            const res = await transcribeAudio(audioBlob);
            handleSendMessage(res.transcription, true); // Mark as voice message
          } catch (err) {
            console.error("Failed to transcribe audio:", err);
            setError("Błąd transkrypcji audio.");
          }
        };
        mediaRecorderRef.current.start();
        setIsRecording(true);
        setRecordingTime(0); // Reset timer
        timerIntervalRef.current = setInterval(() => {
          setRecordingTime((prevTime) => prevTime + 1);
        }, 1000);
      } catch (err) {
        console.error("Failed to start recording:", err);
        setError("Nie można uzyskać dostępu do mikrofonu.");
      }
    }
  };

  const formatRecordingTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString("pl-PL", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div className="chat-window">
      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">👋</div>
            <h2>Cześć!</h2>
            <p>Napisz swoją pierwszą wiadomość...</p>
          </div>
        ) : (
          messages.map((message) => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
                <div className="message-timestamp">
                  {formatTimestamp(message.timestamp)}
                </div>
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="message assistant typing">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="input-area">
        {error && <div className="error-banner">{error}</div>}{" "}
        {/* Moved error banner */}
        {isRecording && (
          <div className="recording-status">
            <span>Nagrywanie...</span>
            <span>{formatRecordingTime(recordingTime)}</span>
          </div>
        )}
        <div className="input-controls">
          {" "}
          {/* New container for input and buttons */}
          <button
            type="button"
            onClick={handleRecord}
            className={`record-button ${isRecording ? "recording" : ""}`}
            disabled={isLoading}
            title={
              isRecording ? "Zatrzymaj nagrywanie" : "Nagraj wiadomość głosową"
            }
          >
            {isRecording ? "⏹️" : "🎙️"}
          </button>
          <form className="message-input-form" onSubmit={handleFormSubmit}>
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Napisz wiadomość..."
              rows="1"
              disabled={isLoading}
              aria-label="Napisz wiadomość"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="send-button"
              title="Wyślij wiadomość"
            >
              {isLoading ? "⏳" : "📤"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default ChatWindow;

import { useState, useRef, useEffect } from "react";
import { useWebSocket } from "../hooks/useWebSocket";
import {
  validateMessage,
  sanitizeMessage,
  formatTimestamp,
} from "../utils/userUtils";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";
import ConnectionStatus from "./ConnectionStatus";
import "./ChatInterface.css";

const ChatInterface = ({ userId }) => {
  const [inputMessage, setInputMessage] = useState("");
  const [isInputFocused, setIsInputFocused] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const {
    isConnected,
    messages,
    isTyping,
    error,
    sendMessage,
    clearMessages,
    clearError,
  } = useWebSocket(userId);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    const message = sanitizeMessage(inputMessage);
    if (!validateMessage(message)) {
      return;
    }

    if (sendMessage(message)) {
      setInputMessage("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleClearChat = () => {
    if (window.confirm("Are you sure you want to clear the chat history?")) {
      clearMessages();
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-title">
          <h2>WiseBot Assistant</h2>
          <p className="chat-subtitle">
            Ask me anything about the uploaded documents
          </p>
        </div>
        <div className="chat-actions">
          <ConnectionStatus isConnected={isConnected} />
          <button
            className="clear-chat-btn"
            onClick={handleClearChat}
            disabled={messages.length === 0}
            title="Clear chat history"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <path d="M3 6h18M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6M8 6V4c0-1 1-2 2-2h4c0-1 1-2 2-2v2" />
              <line x1="10" y1="11" x2="10" y2="17" />
              <line x1="14" y1="11" x2="14" y2="17" />
            </svg>
            Clear
          </button>
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <span className="error-text">{error}</span>
          <button className="error-close" onClick={clearError}>
            ×
          </button>
        </div>
      )}

      <div className="messages-container">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <div className="welcome-icon">🤖</div>
            <h3>Welcome to WiseBot!</h3>
            <p>
              I'm here to help you with information from the uploaded documents.
              Start by asking me a question!
            </p>
            <div className="sample-questions">
              <p>Try asking:</p>
              <ul>
                <li>"Can you summarize the main points regarding _____?"</li>
              </ul>
              and many more... related to your documents.
            </div>
          </div>
        ) : (
          <div className="messages-list">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                timestamp={formatTimestamp(message.timestamp)}
              />
            ))}
            {isTyping && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <form className="message-input-form" onSubmit={handleSubmit}>
        <div className={`input-container ${isInputFocused ? "focused" : ""}`}>
          <textarea
            ref={inputRef}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setIsInputFocused(true)}
            onBlur={() => setIsInputFocused(false)}
            placeholder={isConnected ? "Type your message..." : "Connecting..."}
            disabled={!isConnected}
            rows={1}
            maxLength={1000}
            className="message-input"
          />
          <button
            type="submit"
            disabled={!isConnected || !validateMessage(inputMessage)}
            className="send-button"
            title="Send message"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22,2 15,22 11,13 2,9 22,2" />
            </svg>
          </button>
        </div>
        <div className="input-info">
          <span className="char-count">{inputMessage.length}/1000</span>
          <span className="input-hint">
            Press Enter to send, Shift+Enter for new line
          </span>
        </div>
      </form>
    </div>
  );
};

export default ChatInterface;

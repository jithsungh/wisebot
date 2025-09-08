import { useState, useEffect } from "react";
import "./MessageBubble.css";

const MessageBubble = ({ message, timestamp }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsVisible(true), 50);
    return () => clearTimeout(timer);
  }, []);

  const formatMessageContent = (content) => {
    // Convert markdown-like formatting to HTML
    const formatted = content
      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
      .replace(/\*(.*?)\*/g, "<em>$1</em>")
      .replace(/`(.*?)`/g, "<code>$1</code>")
      .replace(/\n/g, "<br>");

    return { __html: formatted };
  };

  return (
    <div
      className={`message-bubble ${message.type} ${isVisible ? "visible" : ""}`}
    >
      <div className="message-avatar">
        {message.type === "user" ? (
          <div className="user-avatar">👤</div>
        ) : (
          <div className="bot-avatar">🤖</div>
        )}
      </div>
      <div className="message-content">
        <div className="message-header">
          <span className="message-sender">
            {message.type === "user" ? "You" : "WiseBot"}
          </span>
          <span className="message-timestamp">{timestamp}</span>
        </div>
        <div
          className="message-text"
          dangerouslySetInnerHTML={formatMessageContent(message.content)}
        />
      </div>
    </div>
  );
};

export default MessageBubble;

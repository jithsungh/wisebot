import "./TypingIndicator.css";

const TypingIndicator = () => {
  return (
    <div className="typing-indicator">
      <div className="typing-avatar">
        <div className="bot-avatar">🤖</div>
      </div>
      <div className="typing-content">
        <div className="typing-text">
          <span>WiseBot is typing</span>
          <div className="typing-dots">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;

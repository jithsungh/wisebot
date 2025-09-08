import "./ConnectionStatus.css";

const ConnectionStatus = ({ isConnected }) => {
  return (
    <div
      className={`connection-status ${
        isConnected ? "connected" : "disconnected"
      }`}
    >
      <div className="status-indicator"></div>
      <span className="status-text">
        {isConnected ? "Connected" : "Disconnected"}
      </span>
    </div>
  );
};

export default ConnectionStatus;

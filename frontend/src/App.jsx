import { useState, useEffect } from "react";
import ChatInterface from "./components/ChatInterface";
import AdminPanel from "./components/AdminPanel";
import { generateUserId } from "./utils/userUtils";
import "./App.css";

function App() {
  const [userId, setUserId] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Generate or retrieve user ID
    let storedUserId = localStorage.getItem("wisebot_user_id");
    if (!storedUserId) {
      storedUserId = generateUserId();
      localStorage.setItem("wisebot_user_id", storedUserId);
    }
    setUserId(storedUserId);
  }, []);

  if (!userId) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Initializing WiseBot...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1 className="app-title">WiseBot</h1>
        <div className="header-controls">
          <button
            className={`tab-button ${!isAdmin ? "active" : ""}`}
            onClick={() => setIsAdmin(false)}
          >
            Chat
          </button>
          <button
            className={`tab-button ${isAdmin ? "active" : ""}`}
            onClick={() => setIsAdmin(true)}
          >
            Admin
          </button>
        </div>
      </header>

      <main className="app-main">
        {isAdmin ? <AdminPanel /> : <ChatInterface userId={userId} />}
      </main>
    </div>
  );
}

export default App;

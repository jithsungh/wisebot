import { useState, useEffect } from "react";
import webSocketService from "../services/webSocketService";

export const useWebSocket = (userId) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;

    const connect = async () => {
      try {
        await webSocketService.connect(userId);
        setIsConnected(true);
        setError(null);
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
      }
    };

    // Set up event listeners
    const handleMessage = (data) => {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          type: "bot",
          content: data.response,
          timestamp: new Date().toISOString(),
        },
      ]);
      setIsTyping(false);
    };

    const handleTyping = (data) => {
      setIsTyping(data.typing);
    };

    const handleError = (error) => {
      setError(error.message || "WebSocket error occurred");
    };
    const handleConnectionStatus = (status) => {
      setIsConnected(status.connected);
    };

    const handleSystem = (data) => {
      console.log("System message:", data.message);
      // Optionally add system messages to the chat
      if (
        data.message &&
        !data.message.includes("Welcome") &&
        !data.message.includes("Knowledge base")
      ) {
        setMessages((prev) => [
          ...prev,
          {
            id: Date.now(),
            type: "system",
            content: data.message,
            timestamp: new Date().toISOString(),
          },
        ]);
      }
    };

    webSocketService.on("message", handleMessage);
    webSocketService.on("typing", handleTyping);
    webSocketService.on("error", handleError);
    webSocketService.on("connectionStatus", handleConnectionStatus);
    webSocketService.on("system", handleSystem);

    connect();

    return () => {
      webSocketService.off("message", handleMessage);
      webSocketService.off("typing", handleTyping);
      webSocketService.off("error", handleError);
      webSocketService.off("connectionStatus", handleConnectionStatus);
      webSocketService.off("system", handleSystem);
      webSocketService.disconnect();
    };
  }, [userId]);

  const sendMessage = (message) => {
    if (!webSocketService.isConnected()) {
      setError("Not connected to server");
      return false;
    }

    // Add user message to state
    setMessages((prev) => [
      ...prev,
      {
        id: Date.now(),
        type: "user",
        content: message,
        timestamp: new Date().toISOString(),
      },
    ]);

    // Send message via WebSocket
    const success = webSocketService.sendMessage(message);
    if (success) {
      setIsTyping(true);
      setError(null);
    } else {
      setError("Failed to send message");
    }

    return success;
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const clearError = () => {
    setError(null);
  };

  return {
    isConnected,
    messages,
    isTyping,
    error,
    sendMessage,
    clearMessages,
    clearError,
  };
};

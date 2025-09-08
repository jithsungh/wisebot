class WebSocketService {
  constructor() {
    this.socket = null;
    this.listeners = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.isConnecting = false;
  }

  connect(userId) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    if (this.isConnecting) {
      return new Promise((resolve, reject) => {
        const checkConnection = () => {
          if (this.socket?.readyState === WebSocket.OPEN) {
            resolve();
          } else if (!this.isConnecting) {
            reject(new Error("Connection failed"));
          } else {
            setTimeout(checkConnection, 100);
          }
        };
        checkConnection();
      });
    }

    this.isConnecting = true;

    return new Promise((resolve, reject) => {
      try {
        // Connect to FastAPI WebSocket endpoint
        const wsUrl = `ws://localhost:8000/ws/${userId}`;
        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
          console.log("Connected to WebSocket server");
          this.reconnectAttempts = 0;
          this.isConnecting = false;
          this.emit("connectionStatus", { connected: true });
          resolve();
        };

        this.socket.onclose = (event) => {
          console.log("Disconnected from WebSocket server", event);
          this.isConnecting = false;
          this.emit("connectionStatus", { connected: false });

          // Auto-reconnect if not intentionally closed
          if (
            event.code !== 1000 &&
            this.reconnectAttempts < this.maxReconnectAttempts
          ) {
            setTimeout(() => {
              this.reconnectAttempts++;
              this.connect(userId);
            }, this.reconnectDelay);
          }
        };

        this.socket.onerror = (error) => {
          console.error("WebSocket connection error:", error);
          this.isConnecting = false;
          this.reconnectAttempts++;

          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            reject(new Error("Failed to connect after maximum attempts"));
          }
        };

        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error("Error parsing WebSocket message:", error);
          }
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  handleMessage(data) {
    switch (data.type) {
      case "assistant":
        this.emit("message", {
          response: data.message,
          confidence: data.confidence,
          context_count: data.context_count,
        });
        break;
      case "typing":
        this.emit("typing", { typing: true });
        break;
      case "system":
        this.emit("system", data);
        break;
      case "error":
        this.emit("error", { message: data.message });
        break;
      default:
        console.log("Received message:", data);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.close(1000, "User disconnected");
      this.socket = null;
    }
    this.listeners.clear();
    this.isConnecting = false;
  }

  sendMessage(message) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(
        JSON.stringify({
          type: "user",
          message: message,
        })
      );
      return true;
    }
    return false;
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => callback(data));
    }
  }

  isConnected() {
    return this.socket?.readyState === WebSocket.OPEN || false;
  }
}

export default new WebSocketService();

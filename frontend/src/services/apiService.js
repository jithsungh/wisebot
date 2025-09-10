import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Add request interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error("API Error:", error);
        return Promise.reject(error);
      }
    );
  }
  // File upload methods
  async uploadFile(file) {
    const formData = new FormData();
    formData.append("file", file);

    return this.client.post("/upload/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  }

  async processDocumentAsync(file) {
    const formData = new FormData();
    formData.append("file", file);

    return this.client.post("/upload/process-async", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
      timeout: 60000, // 60 seconds for upload
    });
  }

  async getProcessingStatus(processingId) {
    return this.client.get(`/upload/status/${processingId}`);
  }

  async processDocument(file) {
    const formData = new FormData();
    formData.append("file", file);

    return this.client.post("/upload/process", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  }

  // Text processing method
  async processTextInput(text, title = "Manual Text Input") {
    return this.client.post("/upload/process-text", {
      text: text,
      title: title,
    });
  }

  async getUploadedFiles() {
    return this.client.get("/upload/list");
  }

  // Chat methods (for fallback when WebSocket is not available)
  async sendChatMessage(message, userId) {
    return this.client.post("/chat/", {
      message,
      user_id: userId,
    });
  }

  // Health check
  async healthCheck() {
    return this.client.get("/health");
  }
}

export default new ApiService();

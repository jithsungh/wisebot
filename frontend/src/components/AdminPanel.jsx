import { useState, useRef } from "react";
import apiService from "../services/apiService";
import "./AdminPanel.css";

const AdminPanel = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");
  const fileInputRef = useRef(null);

  // Text input states
  const [textInput, setTextInput] = useState("");
  const [textTitle, setTextTitle] = useState("");
  const [isProcessingText, setIsProcessingText] = useState(false);
  const [activeTab, setActiveTab] = useState("file"); // "file" or "text"

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setMessage("");
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setMessage("");
    }
  };

  const validateFile = (file) => {
    const allowedTypes = [
      "application/pdf",
      "application/docx",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/msword",
      "text/plain",
    ];

    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      return "Please select a PDF, Word document, or text file";
    }

    if (file.size > maxSize) {
      return "File size must be less than 10MB";
    }

    return null;
  };

  const uploadAndProcessFile = async () => {
    if (!selectedFile) return;

    const validationError = validateFile(selectedFile);
    if (validationError) {
      setMessage(validationError);
      setMessageType("error");
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setMessage("");

    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const response = await apiService.processDocument(selectedFile);

      clearInterval(progressInterval);
      setUploadProgress(100);

      setTimeout(() => {
        setMessage(
          `Successfully processed "${selectedFile.name}". Created ${response.data.chunks_created} knowledge chunks.`
        );
        setMessageType("success");
        setSelectedFile(null);
        setUploadProgress(0);
        setIsUploading(false);
        if (fileInputRef.current) {
          fileInputRef.current.value = "";
        }
        loadUploadedFiles();
      }, 500);
    } catch (error) {
      setUploadProgress(0);
      setIsUploading(false);
      setMessage(error.response?.data?.detail || "Failed to process document");
      setMessageType("error");
    }
  };

  const processTextInput = async () => {
    if (!textInput.trim()) {
      setMessage("Please enter some text to process");
      setMessageType("error");
      return;
    }

    if (textInput.length > 5 * 1024 * 1024) {
      // 5MB limit
      setMessage("Text is too large. Please limit to 5MB");
      setMessageType("error");
      return;
    }

    setIsProcessingText(true);
    setMessage("");

    try {
      const title = textTitle.trim() || "Manual Text Input";
      const response = await apiService.processTextInput(textInput, title);

      setMessage(
        `Successfully processed text: "${title}". Created ${response.data.chunks_created} knowledge chunks.`
      );
      setMessageType("success");

      // Reset form after success
      setTimeout(() => {
        setTextInput("");
        setTextTitle("");
        setIsProcessingText(false);
        setMessage("");
        setMessageType("");
      }, 3000);
    } catch (error) {
      setIsProcessingText(false);
      setMessage(error.response?.data?.detail || "Failed to process text");
      setMessageType("error");
    }
  };

  const loadUploadedFiles = async () => {
    try {
      const response = await apiService.getUploadedFiles();
      setUploadedFiles(response.data.files || []);
    } catch (error) {
      console.error("Failed to load uploaded files:", error);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString();
  };

  // Load files on component mount
  useState(() => {
    loadUploadedFiles();
  }, []);
  return (
    <div className="admin-panel">
      <div className="admin-header">
        <h2>Admin Panel</h2>
        <p>Upload documents or add text content to the knowledge base</p>
      </div>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === "file" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("file");
            setMessage("");
            setMessageType("");
          }}
        >
          📁 File Upload
        </button>
        <button
          className={`tab-btn ${activeTab === "text" ? "active" : ""}`}
          onClick={() => {
            setActiveTab("text");
            setMessage("");
            setMessageType("");
          }}
        >
          📝 Text Input
        </button>
      </div>

      {/* File Upload Tab */}
      {activeTab === "file" && (
        <div className="upload-section">
          <h3>Upload Document</h3>
          <div
            className={`file-drop-zone ${selectedFile ? "has-file" : ""}`}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileSelect}
              style={{ display: "none" }}
            />

            {selectedFile ? (
              <div className="selected-file">
                <div className="file-icon">📄</div>
                <div className="file-info">
                  <div className="file-name">{selectedFile.name}</div>
                  <div className="file-size">
                    {formatFileSize(selectedFile.size)}
                  </div>
                </div>
                <button
                  className="remove-file"
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedFile(null);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = "";
                    }
                  }}
                >
                  ×
                </button>
              </div>
            ) : (
              <div className="drop-zone-content">
                <div className="upload-icon">📁</div>
                <p>Drop a file here or click to browse</p>
                <p className="file-types">
                  Supports PDF, Word documents, and text files (max 10MB)
                </p>
              </div>
            )}
          </div>

          {isUploading && (
            <div className="upload-progress">
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <div className="progress-text">
                {uploadProgress}% - {message || "Processing..."}
              </div>
            </div>
          )}

          <button
            className="upload-button"
            onClick={uploadAndProcessFile}
            disabled={!selectedFile || isUploading}
          >
            {isUploading ? "Processing..." : "Upload & Process Document"}
          </button>
        </div>
      )}

      {/* Text Input Tab */}
      {activeTab === "text" && (
        <div className="text-section">
          <h3>Add Text Content</h3>

          <div className="text-input-form">
            <div className="input-group">
              <label htmlFor="textTitle">Title (Optional)</label>
              <input
                id="textTitle"
                type="text"
                value={textTitle}
                onChange={(e) => setTextTitle(e.target.value)}
                placeholder="Enter a title for your text content"
                className="title-input"
                maxLength={100}
                disabled={isProcessingText}
              />
              <div className="char-count">{textTitle.length}/100</div>
            </div>

            <div className="input-group">
              <label htmlFor="textContent">Text Content *</label>
              <textarea
                id="textContent"
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste or type your text content here... (max 5MB)

You can include:
• Documentation
• Manuals
• Knowledge articles
• FAQs
• Any text-based information"
                className="text-textarea"
                rows={12}
                disabled={isProcessingText}
              />
              <div className="text-info">
                <span className="char-count">
                  {(textInput.length / 1024 / 1024).toFixed(2)} MB / 5.00 MB
                </span>
                <span className="word-count">
                  {textInput.trim() ? textInput.trim().split(/\s+/).length : 0}{" "}
                  words
                </span>
              </div>
            </div>

            {isProcessingText && (
              <div className="processing-indicator">
                <div className="spinner"></div>
                <span>Processing text content...</span>
              </div>
            )}

            <button
              className="process-button"
              onClick={processTextInput}
              disabled={!textInput.trim() || isProcessingText}
            >
              {isProcessingText ? "Processing..." : "Process Text Content"}
            </button>
          </div>
        </div>
      )}

      {/* Message Display */}
      {message && <div className={`message ${messageType}`}>{message}</div>}

      {/* Files List Section */}
      <div className="files-section">
        <h3>Uploaded Files</h3>
        {uploadedFiles.length === 0 ? (
          <div className="no-files">
            <p>No files uploaded yet. Upload your first document above.</p>
          </div>
        ) : (
          <div className="files-list">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="file-item">
                <div className="file-icon">📄</div>
                <div className="file-details">
                  <div className="file-name">{file.filename}</div>
                  <div className="file-meta">
                    {formatFileSize(file.size)} • Uploaded{" "}
                    {formatDate(file.modified)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;

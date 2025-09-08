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
      // Start async processing
      setMessage("Uploading file...");
      setUploadProgress(10);

      const response = await apiService.processDocumentAsync(selectedFile);
      const processingId = response.data.processing_id;

      setUploadProgress(30);
      setMessage("File uploaded successfully. Processing document...");

      // Poll for processing status
      const pollStatus = async () => {
        try {
          const statusResponse = await apiService.getProcessingStatus(
            processingId
          );
          const status = statusResponse.data;

          setMessage(status.message);

          if (status.status === "uploaded") {
            setUploadProgress(40);
          } else if (status.status === "processing") {
            setUploadProgress(70);
          } else if (status.status === "completed") {
            setUploadProgress(100);
            setMessage(
              `Successfully processed "${selectedFile.name}". Created ${status.chunks_created} knowledge chunks.`
            );
            setMessageType("success");

            // Reset form after success
            setTimeout(() => {
              setSelectedFile(null);
              setUploadProgress(0);
              setIsUploading(false);
              setMessage("");
              setMessageType("");
              if (fileInputRef.current) {
                fileInputRef.current.value = "";
              }
              loadUploadedFiles();
            }, 2000);
          } else if (status.status === "error") {
            setUploadProgress(0);
            setIsUploading(false);
            setMessage(status.message);
            setMessageType("error");
          } else {
            // Continue polling
            setTimeout(pollStatus, 2000);
          }
        } catch (error) {
          console.error("Error polling status:", error);
          setUploadProgress(0);
          setIsUploading(false);
          setMessage("Error checking processing status");
          setMessageType("error");
        }
      };

      // Start polling
      setTimeout(pollStatus, 1000);
    } catch (error) {
      setUploadProgress(0);
      setIsUploading(false);
      setMessage(error.response?.data?.detail || "Failed to process document");
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
        <p>Upload and manage documents for the knowledge base</p>
      </div>

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
        </div>{" "}
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
        {message && <div className={`message ${messageType}`}>{message}</div>}
      </div>

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

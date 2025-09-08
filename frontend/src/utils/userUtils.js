/**
 * Generate a unique user ID
 */
export const generateUserId = () => {
  return `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Format timestamp for display
 */
export const formatTimestamp = (timestamp) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

/**
 * Validate user input
 */
export const validateMessage = (message) => {
  if (!message || typeof message !== "string") {
    return false;
  }
  return message.trim().length > 0 && message.trim().length <= 1000;
};

/**
 * Sanitize user input
 */
export const sanitizeMessage = (message) => {
  return message.trim().replace(/\s+/g, " ");
};

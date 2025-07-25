// Currency formatting utilities for UGX (Ugandan Shillings)

/**
 * Format amount in UGX with proper comma separators
 * @param {number|string} amount - The amount to format
 * @param {boolean} showSymbol - Whether to show the UGX symbol
 * @returns {string} Formatted currency string
 */
export const formatUGX = (amount, showSymbol = true) => {
  if (amount === null || amount === undefined || amount === '') {
    return showSymbol ? 'UGX 0' : '0';
  }

  const numAmount = parseFloat(amount);
  if (isNaN(numAmount)) {
    return showSymbol ? 'UGX 0' : '0';
  }

  // Format with commas for thousands separators
  const formatted = new Intl.NumberFormat('en-UG', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(numAmount);

  return showSymbol ? `UGX ${formatted}` : formatted;
};

/**
 * Format amount in compact form (e.g., 1.2K, 1.5M)
 * @param {number|string} amount - The amount to format
 * @param {boolean} showSymbol - Whether to show the UGX symbol
 * @returns {string} Formatted currency string in compact form
 */
export const formatUGXCompact = (amount, showSymbol = true) => {
  if (amount === null || amount === undefined || amount === '') {
    return showSymbol ? 'UGX 0' : '0';
  }

  const numAmount = parseFloat(amount);
  if (isNaN(numAmount)) {
    return showSymbol ? 'UGX 0' : '0';
  }

  let formatted;
  if (numAmount >= 1000000) {
    formatted = (numAmount / 1000000).toFixed(1) + 'M';
  } else if (numAmount >= 1000) {
    formatted = (numAmount / 1000).toFixed(1) + 'K';
  } else {
    formatted = numAmount.toFixed(0);
  }

  return showSymbol ? `UGX ${formatted}` : formatted;
};

/**
 * Parse UGX string back to number
 * @param {string} ugxString - UGX formatted string
 * @returns {number} Parsed amount
 */
export const parseUGX = (ugxString) => {
  if (!ugxString) return 0;
  
  // Remove UGX prefix and commas
  const cleanString = ugxString.toString()
    .replace(/UGX\s*/i, '')
    .replace(/,/g, '')
    .trim();
  
  const amount = parseFloat(cleanString);
  return isNaN(amount) ? 0 : amount;
};

/**
 * Get currency symbol
 * @returns {string} UGX currency symbol
 */
export const getCurrencySymbol = () => 'UGX';

/**
 * Get currency code
 * @returns {string} Currency code
 */
export const getCurrencyCode = () => 'UGX';

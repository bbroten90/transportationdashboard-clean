import api from './api';

const PDF_API = '/pdf';

const pdfService = {
  /**
   * Extract order data from PDF file
   * @param {File} file - The PDF file
   * @returns {Promise<Object>} Extracted order data
   */
  extractPdfData: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`${PDF_API}/extract`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  /**
   * Extract PDF data and convert to order object
   * @param {File} file - The PDF file
   * @returns {Promise<Object>} Order object
   */
  extractPdfToOrder: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`${PDF_API}/extract-to-order`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  /**
   * Upload PDF file and save to disk
   * @param {File} file - The PDF file
   * @returns {Promise<Object>} Upload result
   */
  uploadPdf: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post(`${PDF_API}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  /**
   * Process PDF file and create order
   * @param {File} file - The PDF file
   * @param {Function} createOrderFn - Function to create order
   * @returns {Promise<Object>} Created order
   */
  processPdfAndCreateOrder: async (file, createOrderFn) => {
    // Extract order data from PDF
    const orderData = await pdfService.extractPdfToOrder(file);
    
    // Create order using the provided function
    return await createOrderFn(orderData);
  },

  /**
   * Validate extracted PDF data
   * @param {Object} extractedData - The extracted data
   * @returns {Object} Validation result
   */
  validateExtractedData: (extractedData) => {
    const errors = {};
    
    // Check required fields
    if (!extractedData.customer_id) {
      errors.customer_id = 'Customer ID is required';
    }
    
    if (!extractedData.customer_name) {
      errors.customer_name = 'Customer name is required';
    }
    
    if (!extractedData.ship_from) {
      errors.ship_from = 'Ship from location is required';
    }
    
    if (!extractedData.ship_to) {
      errors.ship_to = 'Ship to location is required';
    }
    
    if (!extractedData.pickup_date) {
      errors.pickup_date = 'Pickup date is required';
    }
    
    if (!extractedData.weight_kg || extractedData.weight_kg <= 0) {
      errors.weight_kg = 'Valid weight is required';
    }
    
    // Enhanced validation - flag fields that need review
    if (extractedData.needs_review) {
      Object.keys(extractedData.needs_review).forEach(field => {
        if (extractedData.needs_review[field] && !errors[field]) {
          errors[field] = `This field may need review (low confidence)`;
        }
      });
    }
    
    return {
      isValid: Object.keys(errors).length === 0,
      errors
    };
  },
  
  /**
   * Get confidence level description
   * @param {number} score - Confidence score (0-1)
   * @returns {string} Confidence level description
   */
  getConfidenceLevel: (score) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.5) return 'Medium';
    return 'Low';
  },
  
  /**
   * Check if a field needs review based on confidence score
   * @param {number} score - Confidence score (0-1)
   * @returns {boolean} Whether the field needs review
   */
  needsReview: (score) => {
    return score < 0.5;
  }
};

export default pdfService;

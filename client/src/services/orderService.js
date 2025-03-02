import api from './api';

const ORDERS_API = '/orders';

const orderService = {
  /**
   * Create a new transportation order
   * @param {Object} order - The order data
   * @returns {Promise<Object>} Created order
   */
  createOrder: async (order) => {
    const response = await api.post(ORDERS_API, order);
    return response.data;
  },

  /**
   * Get order by ID
   * @param {string} orderId - The ID of the order
   * @returns {Promise<Object>} Order details
   */
  getOrder: async (orderId) => {
    const response = await api.get(`${ORDERS_API}/${orderId}`);
    return response.data;
  },

  /**
   * Get all orders with optional filtering
   * @param {Object} options - Filter options
   * @param {number} options.skip - Number of records to skip
   * @param {number} options.limit - Number of records to return
   * @param {string} options.status - Filter by status
   * @returns {Promise<Array>} Array of orders
   */
  getOrders: async (options = {}) => {
    const { skip = 0, limit = 100, status } = options;
    const params = { skip, limit };
    if (status) params.status = status;
    
    const response = await api.get(ORDERS_API, { params });
    return response.data;
  },

  /**
   * Update order details
   * @param {string} orderId - The ID of the order
   * @param {Object} orderUpdate - The order update data
   * @returns {Promise<Object>} Updated order
   */
  updateOrder: async (orderId, orderUpdate) => {
    const response = await api.put(`${ORDERS_API}/${orderId}`, orderUpdate);
    return response.data;
  },

  /**
   * Delete an order
   * @param {string} orderId - The ID of the order
   * @returns {Promise<boolean>} Success status
   */
  deleteOrder: async (orderId) => {
    const response = await api.delete(`${ORDERS_API}/${orderId}`);
    return response.data;
  },

  /**
   * Filter orders by various criteria
   * @param {Object} filterRequest - Filter criteria
   * @returns {Promise<Array>} Filtered orders
   */
  filterOrders: async (filterRequest) => {
    const response = await api.post(`${ORDERS_API}/filter`, filterRequest);
    return response.data;
  },

  /**
   * Optimize a single order assignment
   * @param {string} orderId - The ID of the order
   * @returns {Promise<boolean>} Success status
   */
  optimizeOrder: async (orderId) => {
    const response = await api.post(`${ORDERS_API}/${orderId}/optimize`);
    return response.data;
  },

  /**
   * Optimize multiple pending orders
   * @param {Object} options - Optimization options
   * @param {string} options.priority - Filter by priority
   * @param {number} options.limit - Number of orders to optimize
   * @returns {Promise<number>} Number of assigned orders
   */
  optimizePendingOrders: async (options = {}) => {
    const response = await api.post(`${ORDERS_API}/batch-optimize`, null, { params: options });
    return response.data;
  },

  /**
   * Get daily order statistics
   * @param {string} date - Optional date (ISO format)
   * @returns {Promise<Object>} Order statistics
   */
  getDailyOrderStats: async (date) => {
    const params = date ? { date } : {};
    const response = await api.get(`${ORDERS_API}/stats/daily`, { params });
    return response.data;
  },

  /**
   * Get orders for a specific date
   * @param {Date} date - The date to get orders for
   * @returns {Promise<Array>} Orders for the date
   */
  getOrdersByDate: async (date) => {
    const fromDate = new Date(date);
    fromDate.setHours(0, 0, 0, 0);
    
    const toDate = new Date(date);
    toDate.setHours(23, 59, 59, 999);
    
    const filterRequest = {
      from_date: fromDate.toISOString(),
      to_date: toDate.toISOString()
    };
    
    return await orderService.filterOrders(filterRequest);
  },

  /**
   * Schedule an order for a specific date
   * @param {string} orderId - The ID of the order
   * @param {Date} pickupDate - The new pickup date
   * @returns {Promise<Object>} Updated order
   */
  scheduleOrder: async (orderId, pickupDate) => {
    const orderUpdate = {
      pickup_date: pickupDate.toISOString()
    };
    
    return await orderService.updateOrder(orderId, orderUpdate);
  }
};

export default orderService;

import api from './api';

const RATES_API = '/rates';

const rateService = {
  /**
   * Get list of available manufacturers
   * @returns {Promise<Array>} Array of manufacturer names
   */
  getManufacturers: async () => {
    const response = await api.get(`${RATES_API}/manufacturers`);
    return response.data.manufacturers;
  },

  /**
   * Get list of warehouses for a manufacturer
   * @param {string} manufacturer - The manufacturer name
   * @returns {Promise<Array>} Array of warehouse names
   */
  getWarehouses: async (manufacturer) => {
    const response = await api.get(`${RATES_API}/warehouses`, { params: { manufacturer } });
    return response.data.warehouses;
  },

  /**
   * Get list of destinations for a manufacturer and warehouse
   * @param {string} manufacturer - The manufacturer name
   * @param {string} warehouse - The warehouse name
   * @returns {Promise<Array>} Array of destination names
   */
  getDestinations: async (manufacturer, warehouse) => {
    const response = await api.get(`${RATES_API}/destinations`, { 
      params: { manufacturer, warehouse } 
    });
    return response.data.destinations;
  },

  /**
   * Calculate rate for a single route
   * @param {Object} request - Rate request
   * @param {string} request.manufacturer - The manufacturer name
   * @param {string} request.warehouse - The warehouse name
   * @param {string} request.destination - The destination name
   * @param {number} request.weight - The weight in kg
   * @returns {Promise<Object>} Rate response
   */
  calculateRate: async (request) => {
    const response = await api.post(`${RATES_API}/calculate`, request);
    return response.data;
  },

  /**
   * Calculate rates for multiple routes
   * @param {Object} request - Bulk rate request
   * @param {Array} request.requests - Array of rate requests
   * @returns {Promise<Object>} Bulk rate response
   */
  calculateBulkRates: async (request) => {
    const response = await api.post(`${RATES_API}/bulk-calculate`, request);
    return response.data;
  },

  /**
   * Get cached rate if available
   * @param {string} manufacturer - The manufacturer name
   * @param {string} warehouse - The warehouse name
   * @param {string} destination - The destination name
   * @param {number} weight - The weight in kg
   * @returns {Promise<Object>} Rate response
   */
  getCachedRate: async (manufacturer, warehouse, destination, weight) => {
    const response = await api.get(`${RATES_API}/rate`, {
      params: { manufacturer, warehouse, destination, weight }
    });
    return response.data;
  },

  /**
   * Calculate distance between two locations
   * @param {string} origin - The origin location
   * @param {string} destination - The destination location
   * @returns {Promise<Object>} Distance in km
   */
  calculateDistance: async (origin, destination) => {
    const response = await api.get(`${RATES_API}/distance`, {
      params: { origin, destination }
    });
    return response.data;
  },

  /**
   * Get coordinates for a location
   * @param {string} location - The location name
   * @returns {Promise<Object>} Location coordinates
   */
  getLocationCoordinates: async (location) => {
    const response = await api.get(`${RATES_API}/coordinates`, {
      params: { location }
    });
    return response.data;
  },

  /**
   * Calculate estimated revenue for a route
   * @param {Object} request - Rate request
   * @returns {Promise<number>} Estimated revenue
   */
  calculateRevenue: async (request) => {
    const rateResponse = await rateService.calculateRate(request);
    return rateResponse.rate;
  },

  /**
   * Calculate total revenue for multiple routes
   * @param {Array} requests - Array of rate requests
   * @returns {Promise<number>} Total estimated revenue
   */
  calculateTotalRevenue: async (requests) => {
    const bulkResponse = await rateService.calculateBulkRates({ requests });
    return bulkResponse.rates.reduce((total, rate) => total + rate, 0);
  }
};

export default rateService;

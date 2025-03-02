import api from './api';

const FLEET_API = '/fleet';

const fleetService = {
  /**
   * Get real-time locations of all vehicles
   * @returns {Promise<Array>} Array of vehicle locations
   */
  getFleetLocations: async () => {
    const response = await api.get(`${FLEET_API}/locations`);
    return response.data;
  },

  /**
   * Get detailed stats for a specific vehicle
   * @param {string} vehicleId - The ID of the vehicle
   * @returns {Promise<Object>} Vehicle stats
   */
  getVehicleStats: async (vehicleId) => {
    const response = await api.get(`${FLEET_API}/vehicles/${vehicleId}/stats`);
    return response.data;
  },

  /**
   * Get list of available trucks
   * @returns {Promise<Array>} Array of available trucks
   */
  getAvailableTrucks: async () => {
    const response = await api.get(`${FLEET_API}/trucks/available`);
    return response.data;
  },

  /**
   * Get list of available trailers
   * @returns {Promise<Array>} Array of available trailers
   */
  getAvailableTrailers: async () => {
    const response = await api.get(`${FLEET_API}/trailers/available`);
    return response.data;
  },

  /**
   * Get current status of an order in Samsara
   * @param {string} orderId - The ID of the order
   * @returns {Promise<string>} Order status
   */
  getOrderStatus: async (orderId) => {
    const response = await api.get(`${FLEET_API}/status/${orderId}`);
    return response.data;
  },

  /**
   * Get fleet utilization metrics
   * @returns {Promise<Object>} Fleet utilization metrics
   */
  getFleetUtilization: async () => {
    const response = await api.get(`${FLEET_API}/utilization`);
    return response.data;
  },

  /**
   * Get list of warehouse locations
   * @returns {Promise<Array>} Array of warehouse locations
   */
  getWarehouseLocations: async () => {
    const response = await api.get(`${FLEET_API}/warehouses`);
    return response.data;
  },

  /**
   * Get available trucks by warehouse
   * @param {string} warehouse - The warehouse location
   * @returns {Promise<Array>} Array of available trucks at the warehouse
   */
  getAvailableTrucksByWarehouse: async (warehouse) => {
    const trucks = await fleetService.getAvailableTrucks();
    return trucks.filter(truck => truck.warehouse === warehouse);
  },

  /**
   * Get available trailers by warehouse
   * @param {string} warehouse - The warehouse location
   * @returns {Promise<Array>} Array of available trailers at the warehouse
   */
  getAvailableTrailersByWarehouse: async (warehouse) => {
    const trailers = await fleetService.getAvailableTrailers();
    return trailers.filter(trailer => trailer.warehouse === warehouse);
  }
};

export default fleetService;

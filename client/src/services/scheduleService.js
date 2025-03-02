import orderService from './orderService';
import rateService from './rateService';
import fleetService from './fleetService';

const scheduleService = {
  /**
   * Get schedule data for a date range
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @returns {Promise<Array>} Schedule data by date
   */
  getScheduleData: async (startDate, endDate) => {
    const dates = [];
    const currentDate = new Date(startDate);
    
    // Generate array of dates
    while (currentDate <= endDate) {
      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    // Get orders for each date
    const scheduleData = await Promise.all(
      dates.map(async (date) => {
        const orders = await orderService.getOrdersByDate(date);
        const stats = await orderService.getDailyOrderStats(date.toISOString());
        
        return {
          date,
          orders,
          stats,
        };
      })
    );
    
    return scheduleData;
  },

  /**
   * Calculate revenue for a specific date
   * @param {Date} date - The date
   * @returns {Promise<number>} Total revenue
   */
  calculateDateRevenue: async (date) => {
    const orders = await orderService.getOrdersByDate(date);
    
    if (!orders.length) {
      return 0;
    }
    
    // Create rate requests for each order
    const rateRequests = orders.map(order => ({
      manufacturer: order.customer_id, // Assuming customer_id is the manufacturer
      warehouse: order.ship_from,
      destination: order.ship_to,
      weight: order.weight_kg
    }));
    
    // Calculate total revenue
    return await rateService.calculateTotalRevenue(rateRequests);
  },

  /**
   * Get resource utilization for a date
   * @param {Date} date - The date
   * @returns {Promise<Object>} Resource utilization
   */
  getResourceUtilization: async (date) => {
    const orders = await orderService.getOrdersByDate(date);
    const warehouses = await fleetService.getWarehouseLocations();
    
    // Initialize warehouse utilization
    const warehouseUtilization = {};
    for (const warehouse of warehouses) {
      const trucks = await fleetService.getAvailableTrucksByWarehouse(warehouse);
      const trailers = await fleetService.getAvailableTrailersByWarehouse(warehouse);
      
      warehouseUtilization[warehouse] = {
        totalTrucks: trucks.length,
        totalTrailers: trailers.length,
        assignedTrucks: 0,
        assignedTrailers: 0,
        utilization: 0
      };
    }
    
    // Count assigned trucks and trailers
    for (const order of orders) {
      if (order.status === 'assigned' || order.status === 'in_transit') {
        const warehouse = order.ship_from;
        if (warehouseUtilization[warehouse]) {
          warehouseUtilization[warehouse].assignedTrucks += 1;
          warehouseUtilization[warehouse].assignedTrailers += 1;
        }
      }
    }
    
    // Calculate utilization percentages
    for (const warehouse in warehouseUtilization) {
      const util = warehouseUtilization[warehouse];
      util.utilization = util.totalTrucks > 0 
        ? (util.assignedTrucks / util.totalTrucks) * 100 
        : 0;
    }
    
    return warehouseUtilization;
  },

  /**
   * Optimize schedule for a date range
   * @param {Date} startDate - Start date
   * @param {Date} endDate - End date
   * @returns {Promise<Object>} Optimization result
   */
  optimizeSchedule: async (startDate, endDate) => {
    const scheduleData = await scheduleService.getScheduleData(startDate, endDate);
    const optimizationResults = [];
    
    // Optimize each day
    for (const dayData of scheduleData) {
      const pendingOrders = dayData.orders.filter(order => order.status === 'pending');
      
      if (pendingOrders.length > 0) {
        const assignedCount = await orderService.optimizePendingOrders({
          limit: pendingOrders.length
        });
        
        optimizationResults.push({
          date: dayData.date,
          pendingOrders: pendingOrders.length,
          assignedOrders: assignedCount,
          success: assignedCount > 0
        });
      } else {
        optimizationResults.push({
          date: dayData.date,
          pendingOrders: 0,
          assignedOrders: 0,
          success: true
        });
      }
    }
    
    return {
      startDate,
      endDate,
      results: optimizationResults,
      totalAssigned: optimizationResults.reduce((sum, day) => sum + day.assignedOrders, 0)
    };
  },

  /**
   * Reschedule an order to a different date
   * @param {string} orderId - Order ID
   * @param {Date} newDate - New pickup date
   * @returns {Promise<Object>} Updated order
   */
  rescheduleOrder: async (orderId, newDate) => {
    return await orderService.scheduleOrder(orderId, newDate);
  },

  /**
   * Calculate optimal schedule for revenue maximization
   * @param {Array} orders - List of orders to schedule
   * @param {Date} startDate - Start date
   * @param {number} days - Number of days to schedule
   * @returns {Promise<Object>} Optimized schedule
   */
  calculateOptimalSchedule: async (orders, startDate, days) => {
    // Get available resources for each day
    const dateRange = [];
    const currentDate = new Date(startDate);
    
    for (let i = 0; i < days; i++) {
      dateRange.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    
    const resourcesByDate = await Promise.all(
      dateRange.map(async (date) => {
        const utilization = await scheduleService.getResourceUtilization(date);
        return { date, resources: utilization };
      })
    );
    
    // Calculate revenue for each order
    const orderRevenues = await Promise.all(
      orders.map(async (order) => {
        const revenue = await rateService.calculateRevenue({
          manufacturer: order.customer_id,
          warehouse: order.ship_from,
          destination: order.ship_to,
          weight: order.weight_kg
        });
        
        return {
          order,
          revenue
        };
      })
    );
    
    // Sort orders by revenue (highest first)
    orderRevenues.sort((a, b) => b.revenue - a.revenue);
    
    // Assign orders to days based on available resources and revenue
    const schedule = resourcesByDate.map(day => ({
      date: day.date,
      orders: [],
      totalRevenue: 0
    }));
    
    for (const { order, revenue } of orderRevenues) {
      const warehouse = order.ship_from;
      
      // Find the best day to schedule this order
      let bestDayIndex = -1;
      
      for (let i = 0; i < schedule.length; i++) {
        const day = schedule[i];
        const resources = resourcesByDate[i].resources[warehouse];
        
        if (!resources) continue;
        
        const assignedCount = day.orders.filter(o => o.ship_from === warehouse).length;
        
        if (assignedCount < resources.totalTrucks) {
          bestDayIndex = i;
          break;
        }
      }
      
      // If we found a day, schedule the order
      if (bestDayIndex >= 0) {
        schedule[bestDayIndex].orders.push(order);
        schedule[bestDayIndex].totalRevenue += revenue;
      }
    }
    
    return {
      startDate,
      days,
      schedule,
      totalRevenue: schedule.reduce((sum, day) => sum + day.totalRevenue, 0)
    };
  }
};

export default scheduleService;

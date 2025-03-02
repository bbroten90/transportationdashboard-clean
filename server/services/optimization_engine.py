import os
from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from ..models.order_models import Order, Truck, Trailer, OrderAssignment
from ..services.samsara_service import SamsaraService
from ..services.rate_service import RateService
from ..services.google_maps_service import GoogleMapsService
from ..services.weather_service import WeatherService
import numpy as np
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

load_dotenv()

class OptimizationEngine:
    def __init__(self):
        self.samsara = SamsaraService()
        self.rate_service = RateService()
        self.google_maps = GoogleMapsService()
        self.weather_service = WeatherService()
        
        # Load optimization settings from environment variables
        self.max_optimization_time = int(os.getenv("MAX_OPTIMIZATION_TIME", "30"))  # seconds
        self.revenue_weight = float(os.getenv("REVENUE_WEIGHT", "0.5"))
        self.cost_weight = float(os.getenv("COST_WEIGHT", "0.3"))
        self.time_weight = float(os.getenv("TIME_WEIGHT", "0.2"))
        
        # Constants for cost calculations
        self.fuel_cost_per_km = 0.35  # Cost in dollars per km
        self.driver_cost_per_hour = 25.0  # Cost in dollars per hour
        self.base_profit_margin = 0.15  # Base profit margin percentage

    async def optimize_assignments(self, orders: List[Order]) -> List[OrderAssignment]:
        """Optimize order assignments using vehicle routing problem solver"""
        # Get available resources
        trucks = await self.samsara.get_available_trucks()
        trailers = await self.samsara.get_available_trailers()
        
        if not trucks or not trailers:
            return []

        # Create distance matrix and time windows
        distance_matrix, time_windows = await self._create_distance_matrix(orders, trucks)
        
        # Create routing index manager
        manager = pywrapcp.RoutingIndexManager(
            len(distance_matrix),
            len(trucks),
            [0] * len(trucks),  # All trucks start at depot
            [0] * len(trucks)   # All trucks end at depot
        )

        # Create routing model
        routing = pywrapcp.RoutingModel(manager)

        # Define cost of each arc
        def distance_callback(from_index, to_index):
            return distance_matrix[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Add time window constraints
        def time_callback(from_index, to_index):
            return time_windows[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

        time_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.AddDimension(
            time_callback_index,
            30,  # Allow waiting time
            1440,  # Maximum time per vehicle (24 hours)
            False,  # Don't force start cumul to zero
            'Time'
        )
        time_dimension = routing.GetDimensionOrDie('Time')

        # Add time window constraints for each location
        for location_idx, time_window in enumerate(time_windows[0]):
            index = manager.NodeToIndex(location_idx)
            time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

        # Add time window constraints for each vehicle start node
        for vehicle_id in range(len(trucks)):
            index = routing.Start(vehicle_id)
            time_dimension.CumulVar(index).SetRange(time_windows[0][0], time_windows[0][1])

        # Setting first solution heuristic
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.FromSeconds(self.max_optimization_time)

        # Solve the problem
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            return self._extract_assignments(solution, routing, manager, orders, trucks, trailers)
        return []

    async def _create_distance_matrix(self, orders: List[Order], trucks: List[Truck]) -> Tuple[List[List[float]], List[List[int]]]:
        """
        Create distance matrix and time windows for optimization using Google Maps API
        
        Args:
            orders: List of orders to optimize
            trucks: List of available trucks
            
        Returns:
            Tuple of (distance_matrix, time_windows)
        """
        # Get all locations (truck warehouses and order pickup/delivery locations)
        locations = [truck.warehouse for truck in trucks] + [order.ship_from for order in orders] + [order.ship_to for order in orders]
        unique_locations = list(dict.fromkeys(locations))  # Preserve order while removing duplicates
        
        # Get distance and time matrices from Google Maps API
        try:
            distance_matrix, time_matrix = await self.google_maps.get_route_matrix(unique_locations)
            print(f"Successfully retrieved distance matrix from Google Maps API for {len(unique_locations)} locations")
        except Exception as e:
            print(f"Error getting distance matrix from Google Maps API: {str(e)}")
            print("Falling back to rate service distance matrix")
            # Fallback to rate service distance matrix
            distance_matrix = await self.rate_service.get_distance_matrix(unique_locations)
            # Create a simple time matrix (assuming 60 km/h average speed)
            time_matrix = [[d / 1000 * 60 for d in row] for row in distance_matrix]
        
        # Get weather data for each location to adjust travel times
        weather_adjustments = await self._get_weather_adjustments(unique_locations)
        
        # Apply weather adjustments to travel times
        for i in range(len(time_matrix)):
            for j in range(len(time_matrix[i])):
                if i != j:  # Skip self-loops
                    # Increase travel time based on weather conditions
                    time_matrix[i][j] *= (1 + weather_adjustments[j])
        
        # Create time windows based on order priorities
        time_windows = []
        for location in unique_locations:
            # Find if this location is an order's ship_from
            order_idx = next((i for i, order in enumerate(orders) if order.ship_from == location), None)
            
            if order_idx is not None:
                order = orders[order_idx]
                if order.priority == "high":
                    time_windows.append([0, 240])  # 4 hours
                elif order.priority == "medium":
                    time_windows.append([0, 480])  # 8 hours
                else:
                    time_windows.append([0, 1440])  # 24 hours
            else:
                # For truck warehouses and other locations
                time_windows.append([0, 1440])  # 24 hours
        
        return distance_matrix, time_windows
    
    async def _get_weather_adjustments(self, locations: List[str]) -> List[float]:
        """
        Get weather-based travel time adjustments for each location
        
        Args:
            locations: List of location names
            
        Returns:
            List of adjustment factors (0.0 = no adjustment, 0.2 = 20% longer travel time, etc.)
        """
        adjustments = []
        
        for location in locations:
            try:
                # Get weather forecast for tomorrow
                weather = await self.weather_service.get_forecast(location, days=1)
                
                if weather and not weather.get("is_placeholder", False):
                    # Extract weather conditions from the forecast
                    conditions = weather["list"][0]["weather"][0]["main"].lower()
                    
                    # Apply adjustments based on weather conditions
                    if "snow" in conditions:
                        adjustments.append(0.3)  # 30% longer in snow
                    elif "rain" in conditions or "shower" in conditions:
                        adjustments.append(0.15)  # 15% longer in rain
                    elif "fog" in conditions or "mist" in conditions:
                        adjustments.append(0.1)  # 10% longer in fog
                    elif "storm" in conditions or "thunder" in conditions:
                        adjustments.append(0.25)  # 25% longer in storms
                    else:
                        adjustments.append(0.0)  # No adjustment for clear weather
                else:
                    # Default to no adjustment if weather data is not available
                    adjustments.append(0.0)
            except Exception as e:
                print(f"Error getting weather for {location}: {str(e)}")
                adjustments.append(0.0)
        
        return adjustments

    def _extract_assignments(self, solution, routing, manager, orders, trucks, trailers) -> List[OrderAssignment]:
        """
        Extract assignments from the solution with cost/revenue optimization
        
        Args:
            solution: OR-Tools solution
            routing: OR-Tools routing model
            manager: OR-Tools routing index manager
            orders: List of orders
            trucks: List of trucks
            trailers: List of trailers
            
        Returns:
            List of optimized order assignments
        """
        assignments = []
        route_metrics = []
        
        # Extract routes and calculate metrics for each vehicle
        for vehicle_id in range(len(trucks)):
            truck = trucks[vehicle_id]
            route = []
            route_orders = []
            total_distance = 0
            total_time = 0
            
            index = routing.Start(vehicle_id)
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route.append(node_index)
                
                if node_index >= len(trucks):  # Skip depot nodes
                    order_index = node_index - len(trucks)
                    if order_index < len(orders):
                        route_orders.append(orders[order_index])
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                
                # Add distance and time between nodes
                if not routing.IsEnd(index):
                    total_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                    total_time += routing.GetArcCostForVehicle(previous_index, index, vehicle_id) / 60  # Convert to minutes
            
            # Calculate revenue, cost, and profit for this route
            revenue = self._calculate_route_revenue(route_orders)
            cost = self._calculate_route_cost(total_distance, total_time)
            profit = revenue - cost
            profit_margin = profit / revenue if revenue > 0 else 0
            
            route_metrics.append({
                'vehicle_id': vehicle_id,
                'truck': truck,
                'route': route,
                'orders': route_orders,
                'total_distance': total_distance,
                'total_time': total_time,
                'revenue': revenue,
                'cost': cost,
                'profit': profit,
                'profit_margin': profit_margin
            })
        
        # Sort routes by profit margin (descending)
        route_metrics.sort(key=lambda x: x['profit_margin'], reverse=True)
        
        # Assign orders based on optimized routes
        for route_metric in route_metrics:
            vehicle_id = route_metric['vehicle_id']
            truck = route_metric['truck']
            route_orders = route_metric['orders']
            
            # Skip routes with negative profit
            if route_metric['profit'] <= 0:
                print(f"Skipping unprofitable route for truck {truck.id} (profit: ${route_metric['profit']:.2f})")
                continue
            
            # Create assignments for each order in the route
            for sequence, order in enumerate(route_orders):
                # Find suitable trailer
                trailer = self._find_suitable_trailer(order, trailers)
                
                if trailer:
                    assignments.append(OrderAssignment(
                        order_id=order.id,
                        truck_id=truck.id,
                        trailer_id=trailer.id,
                        sequence=sequence,
                        assigned_by="OptimizationEngine",
                        assigned_at=datetime.utcnow()
                    ))
                    
                    # Mark trailer as used by reducing its available capacity
                    trailer.current_weight_kg += order.weight_kg
        
        # Print optimization summary
        self._print_optimization_summary(route_metrics, assignments)
        
        return assignments
    
    def _calculate_route_revenue(self, orders: List[Order]) -> float:
        """
        Calculate total revenue for a route
        
        Args:
            orders: List of orders in the route
            
        Returns:
            Total revenue in dollars
        """
        total_revenue = 0.0
        
        for order in orders:
            # Estimate revenue based on weight and distance
            # In a real system, this would come from the rate tables or pricing API
            base_rate = 100.0  # Base rate in dollars
            weight_factor = order.weight_kg / 1000.0  # Convert to tons
            distance_factor = 1.0  # Default distance factor
            
            # Adjust for special requirements
            special_req_factor = 1.0
            for req, value in order.special_requirements.items():
                if value and req == "requires_heating":
                    special_req_factor *= 1.2  # 20% premium for temperature control
                elif value and req == "hazardous":
                    special_req_factor *= 1.5  # 50% premium for hazardous materials
            
            # Calculate order revenue
            order_revenue = base_rate * weight_factor * distance_factor * special_req_factor
            
            # Add to total
            total_revenue += order_revenue
        
        return total_revenue
    
    def _calculate_route_cost(self, distance: float, time: float) -> float:
        """
        Calculate total cost for a route
        
        Args:
            distance: Total distance in kilometers
            time: Total time in minutes
            
        Returns:
            Total cost in dollars
        """
        # Convert distance to kilometers
        distance_km = distance / 1000.0
        
        # Convert time to hours
        time_hours = time / 60.0
        
        # Calculate fuel cost
        fuel_cost = distance_km * self.fuel_cost_per_km
        
        # Calculate driver cost
        driver_cost = time_hours * self.driver_cost_per_hour
        
        # Calculate maintenance cost (simplified)
        maintenance_cost = distance_km * 0.05  # $0.05 per km
        
        # Calculate overhead cost (simplified)
        overhead_cost = 50.0 + (distance_km * 0.02)  # $50 base + $0.02 per km
        
        # Calculate total cost
        total_cost = fuel_cost + driver_cost + maintenance_cost + overhead_cost
        
        return total_cost
    
    def _print_optimization_summary(self, route_metrics: List[Dict[str, Any]], assignments: List[OrderAssignment]) -> None:
        """
        Print a summary of the optimization results
        
        Args:
            route_metrics: List of route metrics
            assignments: List of order assignments
        """
        print("\n===== ROUTE OPTIMIZATION SUMMARY =====")
        print(f"Total routes: {len(route_metrics)}")
        print(f"Total assignments: {len(assignments)}")
        
        total_revenue = sum(route['revenue'] for route in route_metrics)
        total_cost = sum(route['cost'] for route in route_metrics)
        total_profit = sum(route['profit'] for route in route_metrics)
        total_distance = sum(route['total_distance'] for route in route_metrics) / 1000.0  # Convert to km
        total_time = sum(route['total_time'] for route in route_metrics) / 60.0  # Convert to hours
        
        print(f"Total revenue: ${total_revenue:.2f}")
        print(f"Total cost: ${total_cost:.2f}")
        print(f"Total profit: ${total_profit:.2f}")
        print(f"Overall profit margin: {(total_profit / total_revenue * 100) if total_revenue > 0 else 0:.2f}%")
        print(f"Total distance: {total_distance:.2f} km")
        print(f"Total time: {total_time:.2f} hours")
        
        print("\nRoute details:")
        for i, route in enumerate(route_metrics):
            print(f"  Route {i+1} (Truck {route['truck'].id}):")
            print(f"    Orders: {len(route['orders'])}")
            print(f"    Distance: {route['total_distance']/1000:.2f} km")
            print(f"    Time: {route['total_time']/60:.2f} hours")
            print(f"    Revenue: ${route['revenue']:.2f}")
            print(f"    Cost: ${route['cost']:.2f}")
            print(f"    Profit: ${route['profit']:.2f}")
            print(f"    Profit margin: {route['profit_margin']*100:.2f}%")
        
        print("=====================================\n")

    def _find_suitable_trailer(self, order: Order, trailers: List[Trailer]) -> Optional[Trailer]:
        """Find suitable trailer for an order"""
        for trailer in trailers:
            if (trailer.max_weight_kg >= order.weight_kg and
                trailer.warehouse == order.ship_from and
                (not order.special_requirements.get("requires_heating") or trailer.has_pallet_jack)):
                return trailer
        return None

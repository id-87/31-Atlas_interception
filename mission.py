import math
from datetime import datetime , timedelta
from orbital import AtlasTracker
from models import MissionRequest, MissionResult, PropulsionType


class MissionPlanner:
    def __init__(self):
        self.atlas_tracker=AtlasTracker()

        self.propulsion_data={
            PropulsionType.CHEMICAL:{
                "max_delta_v":15,
                "cost_per_kg":50000,
                "efficiency":0.7,
                "min_travel_time":300

            },
            PropulsionType.ELECTRIC:{
                "max_delta_v":25,
                "cost_per_kg":80000,
                "efficiency":0.9,
                "min_travel_time":800
            },
            PropulsionType.NUCLEAR:{
                "max_delta_v":35,
                "cost_per_kg":200000,
                "efficiency":0.85,
                "min_travel_time":250
            },
            PropulsionType.SOLAR_SAIL:{
                "max_delta_v":10,
                "cost_per_kg":30000,
                "efficiency":0.95,
                "min_travel_time":1200
            }
        }

        def plan_mission(self, request:MissionRequest)->MissionResult:
            launch_date=datetime.fromisoformat(request.launch_date)
            atlas_pos_launch = self.atlas_tracker.get_position_at_date(launch_date)
            distance_at_launch = self.atlas_tracker.distance_from_earth(atlas_pos_launch, launch_date)

            base_delta_v = 12 
            intercept_delta_v = distance_at_launch * 1.5  
            total_delta_v = base_delta_v + intercept_delta_v

            prop_specs = self.propulsion_data[request.propulsion_type]
            is_possible = total_delta_v <= prop_specs["max_delta_v"]

            travel_time = max(
            prop_specs["min_travel_time"],
            int(distance_at_launch * 100)
            )

            fuel_efficiency = self._calculate_fuel_efficiency(
            total_delta_v, request.fuel_budget_kg, prop_specs["efficiency"]
            )
        
            mission_cost = self._calculate_cost(
            request.spacecraft_mass_kg, request.fuel_budget_kg, prop_specs["cost_per_kg"]
            )

            intercept_distance = max(1000, 10000 - fuel_efficiency * 1000)  
        
            message = self._generate_message(is_possible, total_delta_v, prop_specs)

            return MissionResult(
            success=is_possible,
            delta_v_required=round(total_delta_v, 2),
            travel_time_days=travel_time,
            fuel_efficiency_score=fuel_efficiency,
            mission_cost_millions=round(mission_cost, 1),
            intercept_distance_km=intercept_distance,
            message=message
            )
        

        def _calculate_fuel_efficiency(self, delta_v: float, fuel_budget: float, efficiency: float) -> int:
            required_fuel = 1000 * math.exp(delta_v / 4.5) - 1000  
            fuel_ratio = fuel_budget / required_fuel
            score = min(10, max(1, int(fuel_ratio * efficiency * 10)))
            return score
        
        def _calculate_cost(self, mass: float, fuel: float, cost_per_kg: float) -> float:
       
            spacecraft_cost = mass * cost_per_kg / 1000000
            fuel_cost = fuel * (cost_per_kg * 0.1) / 1000000
            operations_cost = 50  

            return spacecraft_cost + fuel_cost + operations_cost
        
        def generate_message(self,success:bool,delta_v:float,prop_specs:dict)->str:
            if not success:
                return f" Mission impossible: Requires {delta_v:.1f} km/s but {prop_specs['max_delta_v']} km/s is maximum for this propulsion"
        
            if delta_v < prop_specs["max_delta_v"] * 0.6:
                return f" Excellent mission! Only {delta_v:.1f} km/s required - plenty of fuel margin"
            elif delta_v < prop_specs["max_delta_v"] * 0.8:
                return f" Good mission! {delta_v:.1f} km/s required - moderate fuel usage"
            else:
                return f" Challenging mission! {delta_v:.1f} km/s required - high fuel consumption"



        

    
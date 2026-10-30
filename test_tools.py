from Carbon_coach.carbon_tools import (
    calculate_electricity_emissions,
    calculate_travel_emissions,
    calculate_food_emissions
)

print(calculate_electricity_emissions(10))
print(calculate_travel_emissions(10, "bus"))
print(calculate_food_emissions("rice", 1))
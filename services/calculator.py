"""
Carbon Footprint Calculation Engine
-----------------------------------
This module handles all mathematical and emission factor logic for calculating
monthly and yearly personal greenhouse gas emissions (in kg CO2e and tonnes CO2e).

Emission factors are loaded from `data/emission_factors.json` to keep business
logic decoupled from configuration parameters.
"""

import os
import json
from pathlib import Path

# Base directory for configuration files
BASE_DIR = Path(__file__).resolve().parent.parent
EMISSION_FACTORS_FILE = os.path.join(BASE_DIR, 'data', 'emission_factors.json')

# Default fallback factors in case JSON file is missing or corrupted
DEFAULT_FACTORS = {
    "transportation": {
        "petrol_car": 0.192,
        "diesel_car": 0.171,
        "motorcycle": 0.103,
        "electric_vehicle": 0.053,
        "bus": 0.045,
        "train_metro": 0.032
    },
    "electricity": {
        "kg_co2e_per_kwh": 0.71
    },
    "lpg": {
        "kg_co2e_per_kg": 2.98,
        "default_cylinder_weight_kg": 14.2
    },
    "food": {
        "frequencies_monthly_kg_co2e": {
            "beef": {"rarely": 4.0, "occasionally": 20.0, "frequently": 55.0, "daily": 110.0},
            "chicken": {"rarely": 2.0, "occasionally": 8.0, "frequently": 22.0, "daily": 45.0},
            "fish": {"rarely": 1.5, "occasionally": 6.0, "frequently": 16.0, "daily": 32.0},
            "eggs": {"rarely": 0.5, "occasionally": 2.0, "frequently": 6.0, "daily": 12.0},
            "dairy": {"rarely": 2.0, "occasionally": 8.0, "frequently": 20.0, "daily": 40.0},
            "vegetarian": {"rarely": 1.0, "occasionally": 4.0, "frequently": 10.0, "daily": 20.0},
            "vegan": {"rarely": 0.5, "occasionally": 2.0, "frequently": 5.0, "daily": 10.0}
        }
    },
    "waste": {
        "kg_co2e_per_kg_waste": 0.58,
        "recycling_benefit_rate": 0.60,
        "composting_benefit_rate": 0.35
    },
    "water": {
        "kg_co2e_per_liter": 0.00035,
        "daily_liters_per_person_default": 135.0
    }
}


def load_emission_factors():
    """
    Loads emission factors from data/emission_factors.json.
    Falls back to DEFAULT_FACTORS if the file is unavailable.
    """
    if os.path.exists(EMISSION_FACTORS_FILE):
        try:
            with open(EMISSION_FACTORS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Warning] Could not parse {EMISSION_FACTORS_FILE}: {e}. Using defaults.")
    return DEFAULT_FACTORS


def calculate_transportation(form_data, factors):
    """
    Calculates monthly transportation emissions (kg CO2e).
    Returns 0.0 if the category is disabled or no transit data is entered.
    """
    if form_data.get('include_transportation') == 'no':
        return 0.0
        
    trans_factors = factors.get('transportation', DEFAULT_FACTORS['transportation'])
    
    # 1. Personal Vehicle
    vehicle_type = form_data.get('vehicle_type', 'none')
    try:
        daily_dist = float(form_data.get('vehicle_daily_distance', 0) or 0)
        days_per_month = float(form_data.get('vehicle_days_per_month', 0) or 0)
    except (ValueError, TypeError):
        daily_dist, days_per_month = 0.0, 0.0
    
    daily_dist = max(0.0, min(daily_dist, 1000.0))
    days_per_month = max(0.0, min(days_per_month, 31.0))
    
    personal_monthly_km = daily_dist * days_per_month
    vehicle_factor = trans_factors.get(vehicle_type, 0.0)
    personal_emission = personal_monthly_km * vehicle_factor
    
    # 2. Public Transit (Bus & Train/Metro)
    try:
        bus_km = max(0.0, float(form_data.get('bus_monthly_distance', 0) or 0))
        train_km = max(0.0, float(form_data.get('train_monthly_distance', 0) or 0))
    except (ValueError, TypeError):
        bus_km, train_km = 0.0, 0.0
        
    bus_km = min(bus_km, 5000.0)
    train_km = min(train_km, 10000.0)
    
    bus_emission = bus_km * trans_factors.get('bus', 0.045)
    train_emission = train_km * trans_factors.get('train_metro', 0.032)
    
    total_transport = personal_emission + bus_emission + train_emission
    return round(total_transport, 2)


def calculate_electricity(form_data, factors):
    """
    Calculates monthly electricity emissions (kg CO2e).
    Returns 0.0 if the category is disabled or input is 0/empty.
    """
    if form_data.get('include_electricity') == 'no':
        return 0.0

    elec_factors = factors.get('electricity', DEFAULT_FACTORS['electricity'])
    kwh_factor = elec_factors.get('kg_co2e_per_kwh', 0.71)
    
    try:
        kwh = float(form_data.get('electricity_kwh', 0) or 0)
    except (ValueError, TypeError):
        kwh = 0.0
        
    kwh = max(0.0, min(kwh, 10000.0))
    emission = kwh * kwh_factor
    return round(emission, 2)


def calculate_lpg(form_data, factors):
    """
    Calculates monthly LPG / Cooking Fuel emissions (kg CO2e).
    Returns 0.0 if the category is disabled or input is 0/empty.
    """
    if form_data.get('include_lpg') == 'no':
        return 0.0

    lpg_factors = factors.get('lpg', DEFAULT_FACTORS['lpg'])
    kg_factor = lpg_factors.get('kg_co2e_per_kg', 2.98)
    default_weight = lpg_factors.get('default_cylinder_weight_kg', 14.2)
    
    try:
        cylinders = float(form_data.get('lpg_cylinders_per_month', 0) or 0)
        cylinder_weight = float(form_data.get('lpg_cylinder_size', default_weight) or default_weight)
    except (ValueError, TypeError):
        cylinders = 0.0
        cylinder_weight = default_weight
        
    cylinders = max(0.0, min(cylinders, 50.0))
    cylinder_weight = max(1.0, min(cylinder_weight, 50.0))
    
    emission = cylinders * cylinder_weight * kg_factor
    return round(emission, 2)


def calculate_food(form_data, factors):
    """
    Calculates estimated monthly food emissions (kg CO2e).
    Returns 0.0 if the food category is disabled.
    """
    if form_data.get('include_food') == 'no':
        return 0.0

    food_factors = factors.get('food', DEFAULT_FACTORS['food'])
    freq_table = food_factors.get('frequencies_monthly_kg_co2e', DEFAULT_FACTORS['food']['frequencies_monthly_kg_co2e'])
    
    food_items = ['beef', 'chicken', 'fish', 'eggs', 'dairy', 'vegetarian', 'vegan']
    total_food_emission = 0.0
    
    for item in food_items:
        freq = form_data.get(f'food_{item}', 'rarely')
        if freq == 'none' or freq == 'rarely':
            # Low / zero baseline for rare consumption
            item_table = freq_table.get(item, {})
            emission = item_table.get(freq, 0.0) if freq != 'none' else 0.0
        else:
            item_table = freq_table.get(item, {})
            emission = item_table.get(freq, 0.0)
        total_food_emission += float(emission)
        
    return round(total_food_emission, 2)


def calculate_waste(form_data, factors):
    """
    Calculates estimated monthly household waste emissions (kg CO2e).
    Returns 0.0 if waste category is disabled.
    Formula: (weekly_waste * 4.33 weeks) * emission_factor * reduction_adjustments
    """
    if form_data.get('include_waste') == 'no':
        return 0.0

    waste_factors = factors.get('waste', DEFAULT_FACTORS['waste'])
    kg_waste_factor = waste_factors.get('kg_co2e_per_kg_waste', 0.58)
    recycling_rate = waste_factors.get('recycling_benefit_rate', 0.60)
    composting_rate = waste_factors.get('composting_benefit_rate', 0.35)
    
    try:
        weekly_waste_kg = float(form_data.get('waste_weekly_kg', 0) or 0)
        recycling_pct = float(form_data.get('waste_recycling_pct', 0) or 0)
        does_compost = form_data.get('waste_composting', 'no') == 'yes'
    except (ValueError, TypeError):
        weekly_waste_kg = 0.0
        recycling_pct = 0.0
        does_compost = False
        
    weekly_waste_kg = max(0.0, min(weekly_waste_kg, 200.0))
    recycling_pct = max(0.0, min(recycling_pct, 100.0)) / 100.0
    
    monthly_waste_kg = weekly_waste_kg * 4.333
    base_emissions = monthly_waste_kg * kg_waste_factor
    
    # Apply recycling mitigation
    recycled_reduction = base_emissions * (recycling_pct * recycling_rate)
    # Apply composting mitigation if organic waste is composted
    compost_reduction = base_emissions * (composting_rate if does_compost else 0.0)
    
    final_emissions = max(0.0, base_emissions - recycled_reduction - compost_reduction)
    return round(final_emissions, 2)


def calculate_water(form_data, factors):
    """
    Calculates monthly water supply & pumping emissions (kg CO2e).
    Returns 0.0 if water category is disabled or volume is 0.
    """
    if form_data.get('include_water') == 'no':
        return 0.0

    water_factors = factors.get('water', DEFAULT_FACTORS['water'])
    liter_factor = water_factors.get('kg_co2e_per_liter', 0.00035)
    default_daily_per_person = water_factors.get('daily_liters_per_person_default', 135.0)
    
    water_mode = form_data.get('water_entry_mode', 'people')
    monthly_liters = 0.0
    
    if water_mode == 'direct':
        try:
            monthly_liters = float(form_data.get('water_monthly_liters', 0) or 0)
        except (ValueError, TypeError):
            monthly_liters = 0.0
    else:
        # Estimated by household size
        try:
            val = form_data.get('water_household_people')
            if val is None or val == '':
                return 0.0
            people_count = int(val)
        except (ValueError, TypeError):
            return 0.0
        people_count = max(1, min(people_count, 20))
        monthly_liters = people_count * default_daily_per_person * 30.4
        
    monthly_liters = max(0.0, min(monthly_liters, 200000.0))
    emission = monthly_liters * liter_factor
    return round(emission, 2)


def generate_recommendations(breakdown, largest_category):
    """
    Generates actionable, practical, non-preachy reduction advice
    tailored to the user's highest emission sources.
    """
    suggestions = {
        'transportation': [
            {
                "title": "Adopt Multi-modal Commuting",
                "desc": "Switching even 2 days a week to public transit, metro, cycling, or carpooling can reduce your commuting emissions by over 30%."
            },
            {
                "title": "Maintain Optimal Vehicle Health",
                "desc": "Regular servicing, proper tire inflation, and gentle acceleration improve fuel economy by 10-15%."
            },
            {
                "title": "Explore Electric Mobility",
                "desc": "When upgrading vehicles, consider an electric two-wheeler or EV to drastically cut tailpipe greenhouse gases."
            }
        ],
        'electricity': [
            {
                "title": "Optimize Cooling & AC Setpoints",
                "desc": "Setting your air conditioner to 24°C-26°C instead of 18°C-20°C saves up to 24% electricity per season."
            },
            {
                "title": "Transition to 5-Star & Inverter Appliances",
                "desc": "BEE 5-star rated inverter refrigerators, fans (BLDC), and LED lighting consume up to 50% less power."
            },
            {
                "title": "Harness Solar Rooftop Power",
                "desc": "Explore grid-tied rooftop solar systems (e.g., PM Surya Ghar scheme) to generate clean renewable energy at home."
            }
        ],
        'lpg': [
            {
                "title": "Adopt Fuel-Efficient Cooking Habits",
                "desc": "Using pressure cookers, covering pans with lids, and soaking lentils/beans before boiling reduces LPG consumption by 20%."
            },
            {
                "title": "Use Induction Cooktops for Light Cooking",
                "desc": "Pairing electric induction cookers with clean electricity can lower direct fossil fuel combustion."
            }
        ],
        'food': [
            {
                "title": "Embrace Plant-Rich Meals",
                "desc": "Substituting a few red meat or poultry meals with lentils, legumes, tofu, or paneer can reduce your dietary footprint substantially."
            },
            {
                "title": "Prioritize Local & Seasonal Produce",
                "desc": "Locally grown seasonal foods reduce supply-chain transport and cold storage refrigeration emissions."
            },
            {
                "title": "Prevent Household Food Waste",
                "desc": "Planning meals and smart refrigerator organization prevents wasted food from generating methane in landfills."
            }
        ],
        'waste': [
            {
                "title": "Segregate Waste at Source",
                "desc": "Separate wet (biodegradable) and dry (recyclable) waste cleanly to enable high recovery rates."
            },
            {
                "title": "Start Home or Community Composting",
                "desc": "Composting kitchen scraps diverts organic matter from landfills where it would otherwise decompose anaerobically into methane."
            },
            {
                "title": "Eliminate Single-Use Plastics",
                "desc": "Carry reusable cloth bags, steel water bottles, and refillable containers for daily shopping."
            }
        ],
        'water': [
            {
                "title": "Install Aerators & Water-Saving Fixtures",
                "desc": "Tap aerators and dual-flush toilets reduce water throughput by 40% without compromising water pressure."
            },
            {
                "title": "Fix Plumbing Leaks Promptly",
                "desc": "A single dripping faucet can waste over 30 liters of treated municipal water daily."
            },
            {
                "title": "Rainwater Harvesting",
                "desc": "Recharging groundwater or storing rainwater reduces the municipal pumping energy needed during dry seasons."
            }
        ]
    }
    
    # Gather top 3 recommendations prioritizing the largest category
    recs = []
    if largest_category in suggestions:
        recs.extend(suggestions[largest_category])
        
    # Add suggestions from second highest category if total is less than 3
    sorted_categories = sorted(
        [(k, v) for k, v in breakdown.items() if k != 'other'],
        key=lambda x: x[1],
        reverse=True
    )
    for cat, val in sorted_categories:
        if cat != largest_category and val > 0:
            for s in suggestions.get(cat, []):
                if s not in recs and len(recs) < 4:
                    recs.append(s)
        if len(recs) >= 4:
            break
            
    if not recs:
        recs = [
            {
                "title": "Start with Energy Efficiency",
                "desc": "Switching to LED lighting and 5-star BEE rated appliances is the quickest way to lower household utility emissions."
            },
            {
                "title": "Choose Sustainable Transit",
                "desc": "Prioritizing walking, cycling, or public transit for short trips helps maintain low transport emissions."
            },
            {
                "title": "Practice Mindful Consumption",
                "desc": "Reducing food waste and segregating recyclables preserves natural resources and prevents landfill methane."
            }
        ]
            
    return recs[:3]


def compute_carbon_footprint(form_data):
    """
    Main evaluation function that coordinates category calculations,
    totals, percentages, and recommendations.
    
    Returns a dictionary structured for templates and database storage.
    """
    factors = load_emission_factors()
    
    transportation = calculate_transportation(form_data, factors)
    electricity = calculate_electricity(form_data, factors)
    lpg = calculate_lpg(form_data, factors)
    food = calculate_food(form_data, factors)
    waste = calculate_waste(form_data, factors)
    water = calculate_water(form_data, factors)
    
    total_monthly = round(transportation + electricity + lpg + food + waste + water, 2)
    total_yearly = round(total_monthly * 12.0, 2)
    total_yearly_tonnes = round(total_yearly / 1000.0, 2)
    
    # Calculate percentage contributions
    categories = {
        'transportation': transportation,
        'electricity': electricity,
        'lpg': lpg,
        'food': food,
        'waste': waste,
        'water': water
    }
    
    percentages = {}
    if total_monthly > 0:
        for cat, val in categories.items():
            percentages[cat] = round((val / total_monthly) * 100.0, 1)
        largest_cat = max(categories, key=categories.get)
    else:
        for cat in categories:
            percentages[cat] = 0.0
        largest_cat = 'None'
        
    recommendations = generate_recommendations(categories, largest_cat)
    
    return {
        'transportation': transportation,
        'electricity': electricity,
        'lpg': lpg,
        'food': food,
        'waste': waste,
        'water': water,
        'total_monthly': total_monthly,
        'total_yearly': total_yearly,
        'total_yearly_tonnes': total_yearly_tonnes,
        'percentages': percentages,
        'largest_category': largest_cat,
        'recommendations': recommendations,
        'user_inputs': form_data
    }

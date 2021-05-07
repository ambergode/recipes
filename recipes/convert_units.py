def convert_units(quantity, unit_from, unit_to):    

    # handle unit_from and unit_to incompatibility

    # base units: 
        # volume: ml
        # weight: g

    VOLUME = ['ml', 'liter', 'tsp', 'tbsp', 'cup', 'floz', 'pint', 'quart', 'gallon']
    WEIGHT = ['g', 'kg', 'wtoz', 'lb']
    UNIT = ["", "can"]

    METRIC = ['ml', 'liter', 'g', 'kg']
    AMERICAN = ['tsp', 'tbsp', 'cup', 'floz', 'pint', 'quart', 'gallon', 'wtoz', 'lb']

    # Number by which to multiple (to) or divide (from) to convert from unit to base unit
    CONVERSION_FACTORS = {
        "ml": 1,
        "tsp": 5,
        "tbsp": 15,
        "cup": 250,
        "floz": 30,
        "pint": 500,
        "quart": 950,
        "gallon": 3800,
        "liter": 1000,
        "g": 1,
        "kg": 1000,
        "wtoz": 28.3495,
        "lb": 453.592,
    }

    if unit_from in volume:
        if unit_to not in volume:
            # cannot convert
            return -1
        else:
            # do conversion
            # Convert unit_from to base unit
            pass
    elif unit_from in weight:
        if unit_to not in weight:
            # cannot convert
            return -1
        else:
            # do conversion
            # Convert unit_from to base unit
            pass


    # Temperature

    # TODO
    return ingquant
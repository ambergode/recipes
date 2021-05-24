'''
To convert between volume, weight, and temp units


Some foods can have volume converted to weight, 
but querying the database to see if this is possible should happen before this function

id | food | serving_size | serving_unit | serving_weight
# unconvertable - unit not in volumen/weight lists, size is zero, weight is zero
31|sausage, breakfast sausage, beef, pre-cooked, unprepared|1|UNIT|18.6|
107|carrots, frozen, unprepared|0|undefined|0|
167|pie crust, cookie-type, graham cracker, ready crust|1|UNDETERMINED|28.35|

# convertable
19|milk, lowfat, fluid, 1% milkfat, with added vitamin a and vitamin d|1|CUP|233|
34|peanut butter, smooth style, with salt|2|TBSP|32|
'''

VOLUME = ['ml', 'liter', 'tsp', 'tbsp', 'cup', 'floz', 'pint', 'quart', 'gallon']
WEIGHT = ['g', 'gram', 'kg', 'kilo', 'wtoz', 'lb']
UNIT = ["", "item"]
TEMPERATURE = ['f', 'c']

# eventually - convert from metric to American?
METRIC = ['ml', 'liter', 'g', 'gram', 'kg', 'kilo', 'c']
AMERICAN = ['tsp', 'tbsp', 'cup', 'floz', 'pint', 'quart', 'gallon', 'wtoz', 'lb', 'f']

# Number by which to multiple (to) or divide (from) to convert from unit to base unit
CONVERSION_FACTORS = {
    "ml": 1,
    "tsp": 4.929,
    "tbsp": 14.787,
    "cup": 240,
    "floz": 29.574,
    "pint": 473.176,
    "quart": 946.353,
    "gallon": 3785.41,
    "liter": 1000,
    "g": 1,
    "gram": 1,
    "kg": 1000,
    "kilo": 1000,
    "wtoz": 28.3495,
    "lb": 453.592,
}

def test_get_smaller_unit():
    test_cases = {
        # regular inputs
        'gallon/ml': (get_smaller_unit('gallon', 'ml'), 'ml'),
        'ml/gallon': (get_smaller_unit('ml', 'gallon'), 'ml'),
        'lb/g': (get_smaller_unit('lb', 'g'), 'g'),
        'g/kg': (get_smaller_unit('g', 'kg'), 'g'),
        'liter/cup': (get_smaller_unit('liter', 'cup'), 'cup'),
        'g/wtoz': (get_smaller_unit('g', 'wtoz'), 'g'),
        # same unit
        'g/g': (get_smaller_unit('g', 'g'), 'g'),
        'ml/ml': (get_smaller_unit('ml', 'ml'), 'ml'),
        # weight + volume mix
        'ml/lb': (get_smaller_unit('ml', 'lb'), -1),
        'cup/g': (get_smaller_unit('cup', 'g'), -1),
        # non-weight or volume unit
        'cats/g': (get_smaller_unit('cats', 'g'), -1),
        'ml/cats': (get_smaller_unit('ml', 'cats'), -1),
        'ml/5': (get_smaller_unit('ml', 5), -1),
    }

    passes = 0
    fails = 0

    print('\n\n')
    for key in test_cases.keys():
        actual = test_cases[key][0]
        if actual == test_cases[key][1]:
            result = 'PASS'
            passes += 1
        else:
            result = 'FAIL'
            fails += 1
        print(result, key, 'expected output: ', str(test_cases[key][1]), 'acutal output: ', actual)
    print('\n\n')
    print("PASS:", passes, "     FAIL:", fails)
    print('\n\n')

def get_smaller_unit(unit1, unit2):
    ''' 
    Takes two units and returns the smaller or -1 if they cannot be compared
    ''' 
    try:
        unit1 = unit1.strip().lower()
        unit2 = unit2.strip().lower()
    except:
        return -1

    if (unit1 in VOLUME and unit2 in VOLUME) or (unit1 in WEIGHT and unit2 in WEIGHT):
        unit1_conv = CONVERSION_FACTORS[unit1]
        unit2_conv = CONVERSION_FACTORS[unit2]
        if unit1_conv >= unit2_conv:
            return unit2
        elif unit1_conv < unit2_conv:
            return unit1
    else:
        return -1


def test_convert_units():
    
    test_cases = {
        # volume to volume with int and float
        "convert_units(5, 'ml', 'liter')": (convert_units(5, 'ml', 'liter'), 0.005),
        "convert_units(6, 'tsp', 'tbsp')": (convert_units(6, 'tsp', 'tbsp'), 2.000),
        "convert_units(5, 'cup', 'floz')": (convert_units(5, 'cup', 'floz'), 40.577),
        "convert_units(5, 'pint', 'quart')": (convert_units(5, 'pint', 'quart'), 2.500),
        "convert_units(5, 'gallon', 'ml')": (convert_units(5, 'gallon', 'ml'), 18927.100),
        "convert_units(0.5, 'quart', 'liter')": (convert_units(0.5, 'quart', 'liter'), 0.473),
        "convert_units(0.5, 'pint', 'tsp')": (convert_units(0.5, 'pint', 'tsp'), 48.000),
        "convert_units(0.5, 'cup', 'tbsp')": (convert_units(0.5, 'cup', 'tbsp'), 8.115),
        # weight to weight
        "convert_units(1, 'kg', 'g')": (convert_units(1, 'kg', 'g'), 1000.000),
        "convert_units(5, 'g', 'kg')": (convert_units(5, 'g', 'kg'), 0.005),
        "convert_units(1, 'lb', 'wtoz')": (convert_units(1, 'lb', 'wtoz'), 16.000),
        "convert_units(5, 'wtoz', 'lb')": (convert_units(5, 'wtoz', 'lb'), 0.313),
        "convert_units(5, 'kg', 'wtoz')": (convert_units(5, 'kg', 'wtoz'), 176.370),
        "convert_units(5, 'wtoz', 'g')": (convert_units(5, 'wtoz', 'g'), 141.748),
        # with small numbers
        "convert_units(0.001, 'wtoz', 'g')": (convert_units(0.001, 'wtoz', 'g'), .028),
        "convert_units(0.001, 'liter', 'ml')": (convert_units(0.001, 'liter', 'ml'), 1.000),
        # with big numbers - max digits 7
        "convert_units(5000000, 'liter', 'ml')": (convert_units(5000000, 'liter', 'ml'), 5000000000.000),
        # with fractions
        "convert_units(1/2, 'liter', 'ml')": (convert_units(1/2, 'liter', 'ml'), 500.000),
        "convert_units(1/2, 'cup', 'floz')": (convert_units(1/2, 'cup', 'floz'), 4.058),
        # temp to temp
        "convert_units(100, 'c', 'f')": (convert_units(100, 'c', 'f'), 212.000),
        "convert_units(32, 'f', 'c')": (convert_units(32, 'f', 'c'), 0.000),
        # impossible conversions
        "convert_units(5, 'liter', 'unit')": (convert_units(5, 'liter', 'unit'), -1),
        "convert_units(5, 'gallon', 'f')": (convert_units(5, 'gallon', 'f'), -1),
        "convert_units(5, 'ml', 'g')": (convert_units(5, 'ml', 'g'), -1),
        # non-mass non-volume conversion to self
        "convert_units(5, 'item', 'item')": (convert_units(5, 'item', 'item'), 5),
        # non-number quantity
        "convert_units('q', 'ml', 'lb')": (convert_units('q', 'ml', 'lb'), -1),
        "convert_units('105h', 'g', 'kg')": (convert_units('105h', 'g', 'kg'), -1),
        # negative number quantity for weight/volume
        "convert_units(-5, 'cup', 'pint')": (convert_units(-5, 'cup', 'pint'), -1),
        "convert_units(-5, 'lb', 'g')": (convert_units(-5, 'lb', 'g'), -1),
        # negative number quantity for temp
        "convert_units(-40, 'f', 'c')": (convert_units(-40, 'f', 'c'), -40.000),
        "convert_units(-10, 'c', 'f')": (convert_units(-10, 'c', 'f'), 14.000),
        # same unit
        "convert_units(5, 'tbsp', 'tbsp')": (convert_units(5, 'tbsp', 'tbsp'), 5.000),
        "convert_units(5, 'kg', 'kg')": (convert_units(5, 'kg', 'kg'), 5.000),
        # quantity of zero
        "convert_units(0, 'ml', 'liter')": (convert_units(0, 'ml', 'liter'), 0.000),
        "convert_units(0, 'wtoz', 'lb')": (convert_units(0, 'wtoz', 'lb'), 0.000),
        # non-unit unit
        "convert_units(5, 'cats', 'ml')": (convert_units(5, "cats", 'ml'), -1),
        "convert_units(5, 'ml', 'cats')": (convert_units(5, 'ml', 'cats'), -1),
        # capitalize units
        "convert_units(2, 'tbsp', 'TSP')": (convert_units(2, 'tbsp', 'TSP'), 6.000),
        "convert_units(6, 'TSP', 'TBSP')": (convert_units(6, 'TSP', 'TBSP'), 2.000),
        # units with spaces
        "convert_units(8, 'floz ', ' cup')": (convert_units(8, 'floz ', ' cup'), 0.986),
    }

    epsilon = .09
    fails = 0
    passes = 0

    print('\n\n')
    for key in test_cases.keys():
        actual = test_cases[key][0]
        if abs(actual - test_cases[key][1]) < epsilon:
            result = 'PASS'
            passes += 1
        else:
            result = 'FAIL'
            fails += 1
        print(result, key, 'expected output: ', str(test_cases[key][1]), 'acutal output: ', actual)
    print('\n\n')
    print("PASS:", passes, "     FAIL:", fails)
    print('\n\n')

def convert_units(quantity, unit_from, unit_to):    
    ''' Takes a quantity with up to two decimal places,
    the unit to conver from, and the unit to convert to

    Poduces a float rounded to three decimal points for the converted quantity
    '''
    # normalize units
    unit_from = unit_from.lower().strip()
    unit_to = unit_to.lower().strip()

    # make sure quantity is a number
    try:
        int(quantity)
    except:
        try:
            float(quantity)
        except:
            # quantity is not a number
            return -1
    
    # base units: 
        # volume: ml
        # weight: g

    def do_conversion(quantity):
        
        if quantity < 0:
            return -1

        # numbers are stored in a decimal feild with up to two decimal places
        # multiply by 100 to do integer math
        quantity *= 100

        # Convert unit_from to base_unit
        conversion = float(quantity) * CONVERSION_FACTORS[unit_from]

        # convert base_unit to unit_to
        conversion /= CONVERSION_FACTORS[unit_to]

        # divide by 100
        conversion /= 100
        #round to 3 decimal places
        conversion = round(conversion, 3)
        return conversion

    if unit_from == unit_to:
        return quantity
    elif unit_from in VOLUME:
        if unit_to not in VOLUME:
            # handle unit_from and unit_to incompatibility
            # cannot convert
            return -1
        else:
            return do_conversion(quantity)
    elif unit_from in WEIGHT:
        if unit_to not in WEIGHT:
            # cannot convert
            return -1
        else:
            return do_conversion(quantity)
    elif unit_from in TEMPERATURE:
        if unit_to not in TEMPERATURE:
            # cannot convert
            return -1
        else:
            if unit_from in ['fahrenheit', 'f']:
                return (quantity - 32) * (5/9)
            elif unit_from in ['celsius', 'centigrade', 'c']:
                return (quantity * (9/5)) + 32
    else:
        # cannot convert
        return -1

'''
Potential function to make units more normal - maybe this should just be a django filter?
def unit_conventions(quantity, unit):
    unit = unit.lower().strip()

    if unit in ['ml', 'tsp', 'tbsp']:
        quantity = round(quantity)
    elif unit in ['cup', 'can']:
        whole = int(quantity)
        remainder = quantity % 1
        if remainder <=
        elif remainder <= ((0.25 + (1/3))/2):
            quantity = whole + 0.25
        elif remainder <= (((1/3))

    return quantity, unit
'''


# test_convert_units()
# test_get_smaller_unit()
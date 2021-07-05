strings = ["dairy and egg products","spices and herbs","baby foods","fats and oils","poultry products","soups, sauces, and gravies","sausages and luncheon meats","breakfast cereals","fruits and fruit juices","pork products","vegetables and vegetable products","nut and seed products","beef products","beverages","finfish and shellfish products","legumes and legume products","lamb, veal, and game products","baked products","sweets","cereal grains and pasta","fast foods","meals, entrees, and side dishes","snacks","american indian and alaska native foods","restaurant foods","branded food products database","quality control materials","alcoholic beverages"]

def format_choices(strings):
    for x in strings:
        x = x.strip()
        string =""
        for char in x:
            if char == " ":
                string += "_"
            elif char == ",":
                pass
            else:
                string += char
        
        print(string.upper(), "=", "'" + string + "', _('" + x + "')")


def extract_id(filename):
    import re

    f = open(filename) 
    text = f.read()
    raw_values = re.findall(r"\d\d\d\d", text)
    str_values = set(raw_values)
    values =[]
    for value in str_values:
        values.append(int(value))

    f.close()
    return values

# extract_id("values.txt")

UNIT_DICT = {
    "GRAM": "gram",
    "CUP": "cup",
    "TBSP": "tbsp",
    "TSP": "tsp",
    "WTOZ": "oz",
    "FLOZ": "fl oz",
    "ML": "ml",
    "CAN": "can",
    "GALLON": 'gallon',
    "KILO": "kilo",
    "LITER": "liter",
    "LB": "lb",
    "PINT": 'pint',
    "QUART": 'quart',
    "UNIT": "",
    "UNDETERMINED": "?",
}

CATEGORY_DICT = {
    "alcoholic beverages" : "ALCOHOLIC_BEVERAGES",
    "baby foods" : "BABY_FOODS",
    "baked goods" : "BAKED_PRODUCTS",
    "beef" : "BEEF_PRODUCTS",
    "beverages" : "BEVERAGES",
    "breakfast cereals" : "BREAKFAST_CEREALS",
    "cereals, grains, and pasta" : "CEREAL_GRAINS_AND_PASTA",
    "dairy and eggs" : "DAIRY_AND_EGG_PRODUCTS",
    "fastfoods" : "FAST_FOODS",
    "fats and oils" : "FATS_AND_OILS",
    "fish and shellfish" : "FINFISH_AND_SHELLFISH_PRODUCTS",
    "fruits and fruit juices" : "FRUITS_AND_FRUIT_JUICES",
    "lamb, veal, and game" : "LAMB_VEAL_AND_GAME_PRODUCTS",
    "legumes" : "LEGUMES_AND_LEGUME_PRODUCTS",
    "prepared meals" : "MEALS_ENTREES_AND_SIDE_DISHES",
    "nut and seed" : "NUT_AND_SEED_PRODUCTS",
    "pork" : "PORK_PRODUCTS",
    "poultry" : "POULTRY_PRODUCTS",
    "restaurant foods" : "RESTAURANT_FOODS",
    "sausages and lunch meats" : "SAUSAGES_AND_LUNCHEON_MEATS",
    "snacks" : "SNACKS",
    "soups and sauces" : "SOUPS_SAUCES_AND_GRAVIES",
    "spices and herbs" : "SPICES_AND_HERBS",
    "sweets" : "SWEETS",
    "vegetables" : "VEGETABLES_AND_VEGETABLE_PRODUCTS",
    "other" : "OTHER",
}

def flip_dict(dictionary):
    new_dict = {}
    for key in dictionary.keys():
        value = dictionary[key]
        new_dict[value] = key
    
    print(dictionary, "= {")
    for key in new_dict.keys():
        print('    "' + key + '" : "' + new_dict[key] + '",')
    print("}")
    return new_dict

# flip_dict(CATEGORY_DICT)


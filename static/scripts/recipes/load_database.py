import csv
import sqlite3
import os

from recipes.models import Ingredient


# function takes a name (csv file and table)
def load_database(location, filename):
    with open((location + "/" + filename), newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        # connect to database
        con = sqlite3.connect('RawFoodDatabase.db')
        # create a cursor (see https://docs.python.org/3/library/sqlite3.html)
        db = con.cursor()

        def log_row(row):
            # INSERT line into table
            command = "INSERT INTO " + filename[:-4] + " VALUES ("
            for i in range(len(row)):
                command += '"' + str(row[i]).strip().lower() + '"' + ", "
            command = command[:-2] + ")"
            # print(command)
            db.execute(command)
            con.commit()

        row1 = []
        first_line = True
        second_line = False
        print("\nLoading file:", filename)
        for row in reader:
            if first_line == True:
                row1 = row
                first_line = False
                second_line = True
            elif second_line == True:
                # establish type of entry for each column in row
                entry_type =[]
                for entry in row:

                    if entry =="":
                        entry_type.append("TEXT")
                    else:   
                        try:
                            int(entry)
                            entry_type.append("INTEGER")
                        except:
                            try:
                                float(entry)
                                entry_type.append("REAL")
                            except:
                                entry_type.append("TEXT")

                # create a new table with name of file
                # create cols with header values and types from row 2
                command = "CREATE TABLE IF NOT EXISTS " + filename[:-4] + "("
                for i in range(len(row1)):
                    command += str(row1[i]).lower().strip() + " " + entry_type[i] + ", "
                command = command[:-2]
                command += ")"
                print("\nCreating new table with", command, "\n")
                db.execute(command)
                
                # Log the 2nd row
                log_row(row)
                second_line = False
            else:
                log_row(row)
    return 

# Remove "legacy_foods" if want access to all the rest of the files            
# files = os.listdir('FoodDatabase/csvs/legacy_foods')
# files.remove(".DS_Store")
# To remove already processed files from the list
# remove = [
#     "food_calorie_conversion_factor.csv", 
#     "food_nutrient_derivation.csv",
#     "food_nutrient_conversion_factor.csv",
#     "foundation_food.csv",
#     "measure_unit.csv",
#     "nutrient.csv",
#     "food.csv",
#     "wweia_food_category.csv",
#     "fndds_ingredient_nutrient_value.csv",
# ]
# for file in remove:
#     if file in files:
#         files.remove(file)

# load_database("csvs", "input_food.csv")

# for f in files:
#     load_database("FoodDatabase/csvs/legacy_foods", f)

def load_django_database(): 

    # Select fdc_id from each foundation foods
    # connect to RawFoodDatabase
    conn = sqlite3.connect('RawFoodDatabase.db')
    cur = conn.cursor()

    cur.execute("SELECT DISTINCT(description), fdc_id FROM food WHERE data_type = 'sr_legacy_food' OR data_type = 'foundation_food'")
    rows = cur.fetchall()
    food_ids = []
    for row in rows:
        food_ids.append(row[1])


    # for each food id found, search for pertinant info
    for food_id in food_ids:
    # for i in range(1):        # for troubleshooting only
        # food_id = 168794
        print("Adding ", food_id)
        # name, category
        command = "SELECT DISTINCT(food.description), food_category.description FROM food \
            JOIN food_category ON food_category.id = food.food_category_id \
            WHERE food.fdc_id = " + str(food_id)
        cur.execute(command)
        base_info = cur.fetchall()

        # nutrient names, amounts and units
        command = "SELECT DISTINCT(nutrient.id), food_nutrient.amount, nutrient.unit_name \
            FROM ((food \
            JOIN food_nutrient ON food.fdc_id = food_nutrient.fdc_id) \
            JOIN nutrient_incoming_name AS nin ON nin.nutrient_id = food_nutrient.nutrient_id) \
            JOIN nutrient ON nin.nutrient_id = nutrient.id \
            WHERE food.fdc_id = " + str(food_id) + \
            " AND nin.nutrient_id IN (1093, 1079, 1292, 1004, 1003, 1008, 1293, 1005, 2033, 1258, 1253, 1257, 1063)"
        cur.execute(command)
        nutrient_info = cur.fetchall()

        # typical serving size, unit, weight in grams
        command = "SELECT DISTINCT(measure_unit.name), food_portion.amount, food_portion.gram_weight \
            FROM food_portion JOIN measure_unit ON measure_unit.id = food_portion.measure_unit_id \
            WHERE fdc_id = " + str(food_id) + " LIMIT 1"
        cur.execute(command)
        serving_info = cur.fetchall()
        
        # check to make sure food name is not already in database
        if Ingredient.objects.filter(ingredient = base_info[0][0]):
            pass
        else:
            new_food = Ingredient()
            if len(base_info) > 0:
                new_food.ingredient = base_info[0][0]
                new_food.category = base_info[0][1]
            if len(serving_info) > 0:
                new_food.typical_serving_size = round(serving_info[0][1], 2)

                # normalize units
                unit_dict = {
                    "liter": 'LITER',
                    "cup": 'CUP',
                    "gallon": "GALLON",
                    "pint": "PINT",
                    "lb": "LB",
                    "fl oz": "FLOZ",
                    "oz": "WTOZ",
                    "quart": "QUART",
                    "teaspoon": "TSP",
                    "tablespoon": "TBSP",
                    "tablespoons": "TBSP",
                    "undetermined": "UNDETERMINED",
                }
                unit = serving_info[0][0].lower().strip()
                if unit in unit_dict.keys():
                    unit = unit_dict[unit]
                else:
                    unit = "UNIT"

                new_food.typical_serving_unit = unit
                new_food.weight_per_serving = round(serving_info[0][2], 2)

            # assign values for each nutrient
            if len(nutrient_info) > 0:
                for nutrient in nutrient_info:
                    if len(nutrient) > 0:
                        nutrient_id = nutrient[0]
                        nutrient_val = round(nutrient[1], 2)
                        # print(nutrient_val)
                        if nutrient_id == 1003: new_food.protein = nutrient_val
                        elif nutrient_id == 1004: new_food.fat = nutrient_val
                        elif nutrient_id == 1005: new_food.carbs = nutrient_val
                        elif nutrient_id == 1008: new_food.calories = nutrient_val
                        elif nutrient_id == 1063: new_food.sugar = nutrient_val
                        elif nutrient_id == 1079: new_food.fiber = nutrient_val
                        elif nutrient_id == 1093: new_food.sodium = nutrient_val
                        elif nutrient_id == 1253: new_food.cholesterol = nutrient_val
                        elif nutrient_id == 1257: new_food.transfats = nutrient_val
                        elif nutrient_id == 1258: new_food.satfats = nutrient_val
                        elif nutrient_id == 1292: new_food.monounsatfats = nutrient_val
                        elif nutrient_id == 1293: new_food.polyunsatfats = nutrient_val
                        elif nutrient_id == 2033: new_food.fiber = nutrient_val
            # print(base_info, nutrient_info, serving_info)
            new_food.save()
    
    return 0

load_django_database()
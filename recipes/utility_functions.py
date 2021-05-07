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


def extract_id(filename)
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
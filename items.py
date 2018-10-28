import random
import re
import fileinput
import os
import glob
from shutil import copyfile

import yaml

from card import *

options = []
properties = []


def generate_yaml():
    if os.path.exists("yaml/items.yaml"):
        return

    for directory, subdirectories, files in os.walk("yaml"):

        # skip yaml base directory
        if directory is "yaml":
            continue

        file_list = glob.glob(os.path.join(directory, "*.yaml"))

        # if no files exist, continue
        if file_list is []:
            continue

        file_name = "{}.yaml".format(directory)
        with open(file_name, 'w') as file:
            input_lines = fileinput.input(file_list)
            current_file_name = input_lines._files[0]
            current_file_line = "{}:\n".format(current_file_name.split('/')[-1].split(".")[0])
            modified_lines = [current_file_line]
            for line in input_lines:
                if input_lines.filename() is not current_file_name:
                    current_file_name = input_lines.filename()
                    current_file_line = "{}:\n".format(current_file_name.split('/')[-1].split(".")[0])
                    modified_lines.append(current_file_line)
                modified_line = re.sub("^", "  ", line)
                modified_lines.append(modified_line)
            file.writelines(modified_lines)

        # check if it is the properties directory to create the nodc file
        if directory.endswith("properties"):
            nodc_file_name = "yaml/properties_nodc.yaml"
            copyfile("yaml/properties.yaml", nodc_file_name)

            for line in fileinput.input(nodc_file_name, inplace=True):
                modified_line = re.sub("[Dd][Cc] ?[0-9]+ ?", "", line)

                # fix the case for a {} Intelligence check, where removing DC makes the sentence wrong
                print(re.sub("a ([aAeEiIoOuU])", "an \g<1>", modified_line), end='')

def generate_items(type_name, property1, property2, quantity):

    max_length = max(type_name.__len__() if type(type_name) is list else 1,
                     property1.__len__() if type(property1) is list else 1,
                     property2.__len__() if type(property2) is list else 1,
                     quantity.__len__() if type(quantity) is list else 1)

    if type(type_name) is list:
        if not type_name.__len__() == max_length:
            raise Exception("item is a list but is not the same length as the largest")
    else:
        type_name = [type_name] * max_length

    if type(property1) is list:
        if not property1.__len__() == max_length:
            raise Exception("property1 is a list but is not the same length as the largest")
    else:
        property1 = [property1] * max_length

    if type(property2) is list:
        if not property2.__len__() == max_length:
            raise Exception("property2 is a list but is not the same length as the largest")
    else:
        property2 = [property2] * max_length

    if type(quantity) is list:
        if not quantity.__len__() == max_length:
            raise Exception("quantity is a list but is not the same length as the largest")
    else:
        quantity = [quantity] * max_length

    generate_yaml()

    global options
    global properties
    # read in the options for generation
    options = yaml.load(open("yaml/items.yaml"))
    properties = yaml.load(open("yaml/properties.yaml"))

    items = []

    for typ, prop1, prop2, quant in zip(type_name, property1, property2, quantity):
        items += [generate_item(typ, prop1, prop2) for _ in range(quant)]

    return items


def generate_item(item_class, property1, property2):
    item_class = "Wonderous item" if item_class == "trinket" else item_class.capitalize()

    ops = options[item_class]

    if not ops:
        return []

    props = properties[item_class]

    if not props:
        return []

    name = ""
    effect = ""

    if property1 and property1 == "weak":
        prop = random.choice(props)
        name = str(prop["prop1"])
        effect += prop["effect"].strip()

    item_ops = random.choice(ops)

    item = random.choice(item_ops) if type(item_ops) == list else item_ops

    typ = "{}{}".format(item_class, "({})".format(item_ops[0]) if type(item_ops) == list else "")

    name += " " + item if name != "" else item

    if item_class != "Wonderous item":
        slot = item_class
    elif re.search('Helm|Cap|Hat|Circlet|Mask|Tiara', name, re.IGNORECASE):
        slot = "Head"
    elif re.search('Gauntlets|Bracers', name, re.IGNORECASE):
        slot = "Wrist"
    elif re.search('Boots', name, re.IGNORECASE):
        slot = "Feet"
    elif re.search('Collar|Amulet|Pendant|Medallion', name, re.IGNORECASE):
        slot = "Neck"
    else:
        expression = re.compile('(Belt|Ring|Cloak|Gloves)')
        match = expression.search(name)
        slot = match.group(1) if match else ""

    if property2 and property2 == "weak":
        prop = random.choice(props)
        name += " " + str(prop["prop2"])
        effect += "{}{}".format("\n" if effect != "" else "", prop["effect"].strip())

    return {
        "name": name,
        "type": typ,
        "rarity": "Uncommon",
        "attunement": "TRUE",
        "slot": slot,
        "value": "",
        "cursed": "",
        "effect": effect
    }


items = generate_items(["wonderous item", "armor"], ["weak", None], [None, "weak"], 1)

write_to_file(make_cards(items))

# TODO add flags framework
# TODO add flags to use properties with or without dc

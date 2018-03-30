import yaml
import random


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

    items = []

    for typ, prop1, prop2, quant in zip(type_name, property1, property2, quantity):
        items += [generate_item(typ, prop1, prop2) for _ in range(quant)]

    return items


def generate_item(item_type, property1, property2):
    # read in the options for generation
    options = yaml.load(open("items.yaml"))
    properties = yaml.load(open("properties.yaml"))

    item_type = "Wonderous item" if item_type == "trinket" else item_type.capitalize()

    ops = options[item_type]

    if not ops:
        return []

    props = properties[item_type]

    if not props:
        return []

    name = ""
    effect = ""

    if property1 and property1 == "weak":
        prop = random.choice(props)
        name = prop["prop1"]
        effect += prop["effect"].strip()

    item_ops = random.choice(ops)

    item = random.choice(item_ops) if type(item_ops) == list else item_ops

    typ = "{}{}".format(item_type, "({})".format(item_ops[0]) if type(item_ops) == list else "")

    name += " " + item if name != "" else item

    if property2 and property2 == "weak":
        prop = random.choice(props)
        name += " " + prop["prop2"]
        effect += "{}{}".format("\n" if effect != "" else "", prop["effect"].strip())

    return {
            "name": name,
            "type": typ,
            "rarity": "Uncommon",
            "attunement": "TRUE",
            "slot": item_type,
            "value": "",
            "cursed": "",
            "effect": effect
        }


def format_item_as_table_string(item):
    return """<table>
<tr><th>{}</th></tr>
<tr class='type'><td><em>{}</em>, <em>{}<br/>{}</em></td></tr>
{}
{}
</table>"""\
    .format(item["name"],
            # add the type, if there is one, e.g., wonderous item or Armor
            "<em>{}</em>".format(item["type"]) if item["type"] else "",

            # every item should have a rarity
            item["rarity"],

            # format requires attunement or requirements, if the item needs attunement
            "(requires {})".format("attunement"
                                   if item["attunement"] is "TRUE"
                                   else item["attunement"])
            if item["attunement"] else "",

            # add slot and value row, if one of them exists
            "<tr class='slot'><td>{}<em>Value: {}</em></td></tr>"
            .format("<em>Slot: {}</em>\t".format(item["slot"]) if item["slot"] else "",
                    item["value"] if item["value"] else "-------")
            if item["slot"] or item["value"] else "",

            # if the item has no effect, i.e., is just a long sword, don't add an effect layer
            "<tr><td class='effect'>{}</td></tr>".format(item["effect"]) if item["effect"] else "")


def get_styling():
    return """<style>
  div>table{
    margin: 5px;
    page-break-inside: avoid;
  }
  tbody {
    width: 100px !important;
  }
  table {
    width: 100%;
    border: 1px solid black;
    border-collapse: collapse;
    text-align: center;
  }
  tr, td {
    border: 1px solid black;
    border-collapse: collapse;
    text-align: center;
  }
  li {
   text-align: left;
  }
  .type, .slot {
    background-color: #d9d9d9;
  }
  .effect {
    padding: 5px
  }
  .column {
    float: left;
    width: 49%;
    padding: 2px;
  }
  th {
    background-color: #ffffcc;
  }

@page { margin: 0.5cm } /* All margins set to 2cm */

  /* Clear floats after the columns */
  .row:after {
    content: "";
    display: table;
    clear: both;
  }
</style>
"""


def make_cards(items):

    # to alternate between the lists
    index = 0

    # items that will go in the right column
    right_items = ""
    # items that will go at the bottom because they are too long
    bottom_items = ""

    # the string that will be all the html tables
    html_string = get_styling() + "\n<div class='row'>\n<div class='column'>\n"

    for item in items:
        if index % 2 != 0:
            # add to right list
            right_items += format_item_as_table_string(item)
        elif item["effect"].__len__() > 1830:
            # effect is too long, add to bottom
            bottom_items += format_item_as_table_string(item)
        else:
            # will go in the left column, so we can just add it directly
            html_string += format_item_as_table_string(item)
        index += 1

    # add column change, items in right column, and items too long to be in a column
    return html_string + "\n</div>\n<div class='column'>{}</div>\n{}</div>".format(right_items, bottom_items)


# with open("items.html", "w") as html_page:
#     html_page.write(make_cards(generate_items(["wonderous item", "armor"], ["weak", None], [None, "weak"], 1)))

print(generate_items(["wonderous item", "armor"], ["weak", None], [None, "weak"], 1))
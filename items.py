import requests
from bs4 import BeautifulSoup
import re


def create_request_objects(item, property1, property2, quantity):

    max_length = max(item.__len__() if type(item) is list else 1,
                     property1.__len__() if type(property1) is list else 1,
                     property2.__len__() if type(property2) is list else 1,
                     quantity.__len__() if type(quantity) is list else 1)

    if type(item) is list:
        if not item.__len__() == max_length:
            raise Exception("item is a list but is not the same length as the largest")
    else:
        item = [item] * max_length

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

    return [dict(zip(["item", "prop1", "prop2", "quantity"], x))
            for x in list(zip(item, property1, property2, quantity))]


def get_items(item, property1, property2, quantity):
    url = "http://www.lordbyng.net/inspiration/results.php"

    # create lists of requests to make

    reqs = create_request_objects(item, property1, property2, quantity)

    plain_text = ""

    for req in reqs:
        html_response = requests.post(url, req)
        plain_text += html_response.text

    # when using two properties, there is not a line break like there is with one, which screws up parsing
    soup = BeautifulSoup(plain_text.replace("</p><p>", "</p>\n<p>"))

    items = []

    for item_object in filter(lambda x: not re.search("DMG", x.text), soup.findAll('div', {"class": 'weapon'})):
        # get nonempty lines
        lines = list(filter(None, item_object.text.splitlines()))

        # get name
        name = re.sub("\d+: ", "", lines[0])

        # get type and rarity
        try:
            type_name, rarity = lines[1].split(",")[0:2] if lines[1].split(",").__len__() > 1\
                else (lines[1].split(",")[0], "common")
        except Exception as ex:
            print(ex)
            print(lines[1].split(","))
            print(item_object.text)
            continue

        # there will be a space after the comma, at the beginning of rarity, as well as a (requires Attunement) after it
        # so just extract rarity
        rarity, attunement = rarity.split(" ")[1::2] if rarity is not "common" else (rarity, "")
        attunement = "TRUE" if re.search("Attunement", attunement, re.IGNORECASE) else ""

        # get effect(s)
        # replace with break so it works in html
        effect = "<br>".join(lines[2:])

        # determine slot
        if re.match("Armor", type_name):
            slot = "Armor"
        elif re.match("Weapon", type_name):
            slot = "Weapon"
        else:
            if re.search('Helm|Cap|Hat|Circlet|Mask|Tiara', name, re.IGNORECASE):
                slot = "Head"
            elif re.search('Gauntlets|Bracers', name, re.IGNORECASE):
                slot = "Wrist"
            elif re.search('Boots', name, re.IGNORECASE):
                slot = "Feet"
            elif re.search('Collar|Necklace|Amulet|Pendant|Medallion', name, re.IGNORECASE):
                slot = "Neck"
            else:
                expression = re.compile('(Belt|Ring|Cloak|Gloves)')
                match = expression.search(name)
                slot = match.group(1) if match else ""

        items.append({
            "name": name,
            "type": type_name,
            "rarity": rarity,
            "attunement": attunement,
            "slot": slot,
            "value": "",
            "cursed": "",
            "effect": effect
        })
        if not slot:
            print(name, type_name, rarity, "TRUE", slot, "", "", effect, sep='\t')

    return items


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


with open("items.html", "w") as html_page:
    html_page.write(make_cards(get_items(["trinkets", "armor"], ["weak", "none"], ["none", "weak"], 1)))

def format_item_as_table_string(item):
    return """<table>
<tr><th>{}</th></tr>
<tr class='type'><td><em>{}</em>, <em>{}<br/>{}</em></td></tr>
{}
{}
</table>""" \
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


def write_to_file(cards, file="items.html"):
    with open(file, "w") as html_page:
        html_page.write(cards)

"""Simple Modbus Map register lookup web application.

@author Sam Pottinger
@license GNU GPL v2
"""

import json
import os

import flask
from flask import Markup, request

from ljm_constants import ljmmm
import lj_scribe
import parse_ljsl
import serialize

app = flask.Flask(__name__)

reg_data_compressed = ljmmm.get_registers_data(expand_names=False, inc_orig=False)
reg_data_expanded = ljmmm.get_registers_data(expand_names=True, inc_orig=False)
modbus_maps = ljmmm.get_device_modbus_maps()
reg_maps = ljmmm.get_device_modbus_maps(expand_names=True, inc_orig=True)
ALL_DEVICES_NAME = u"All Devices"
ALL_TAGS_NAME = u"All Tags"
INVALID_FILTER_ARGUMENTS = ["null", "undefined"]
OPTION_TAG_TEMLPATE = "<option value=\"{tag}\">{tag}</option>"
SELECTED_OPTION_TAB_TEMPLATE = "<option value=\"{tag}\" selected=\"selected\">" \
    "{tag}</option>"
ALLOWED_REDISPLAY_DOMAIN = "https://labjack.com"
# NO_TAGS_NAME = "No Tags"


@app.route("/")
def show_ui():
    """Display the JavaScript client for viewing MODBUS map information.
    
    @return: HTML register lookup table and controls.
    @rtype: str
    """

    device_options = modbus_maps.keys()
    device_options.insert(0, ALL_DEVICES_NAME)

    tag_options = set()
    for x in modbus_maps:
        for reg in modbus_maps[x]:
            for tag in reg["tags"]:
                tag_options.add(tag)
    tag_options = sorted(list(filter(None, tag_options)))

    tag_options = [Markup(OPTION_TAG_TEMLPATE).format(tag=tag)
        for tag in tag_options]

    tag_options.insert(0,
        SELECTED_OPTION_TAB_TEMPLATE.
        format(tag=ALL_TAGS_NAME)
    )
    
    return flask.render_template(
        "simple_register_lookup.html",
        device_names = device_options,
        tags = tag_options
    )


def prepareFilterArg(argument):
    """Parse the value of a filter argument.
    
    Reject filter arguments that were given invalid values in the request like
    null or undefined. If it is a valid value, split a list of filter arguments
    (eventually joined by AND), by commas.
    
    @return: List of parsed filter arguments.
    @rtype: list
    """
    if argument in INVALID_FILTER_ARGUMENTS:
        return []

    return argument.split(",")


@app.route("/lookup.html")
def embed_lookup():
    """Render an embeded registers information table based on query params.
    
    @return: Rendered HTML with device info that can be embedded.
    @rtype: str
    """
    show_embed_controls = flask.request.args.get("show-embed", "true") == "true"
    values = {
        "devices": request.args.get("devices", ALL_DEVICES_NAME),
        "tags": request.args.get("tags", ALL_TAGS_NAME),
        "not_tags": request.args.get("not-tags", "null"),
        "add_reg_names": request.args.get("add-reg-names", "null"),
        "add_regs": request.args.get("add-regs", "null"),
        "expand-addresses": request.args.get("expand-addresses", "null"),
        "fields": request.args.get("fields", "null"),
        "show_embed_controls": show_embed_controls
    }
    return flask.render_template("embed_lookup.html", **values)


def match_device(reg, device_name):
    for dev in reg['devices']:
        if dev['device'] == device_name:
            return True


@app.route("/lookup.json")
def lookup():
    """Render JSON formatted device MODBUS map.
    
    Render a JSON listing of filtered MODBUS map records for use in external
    applications or by the simple register lookup tool itself.
    
    @return: JSON encoded MODBUS map records.
    @rtype: str
    """

    # Parse user query parameters
    device_name = request.args.get("device_name", ALL_DEVICES_NAME)
    tags = prepareFilterArg(request.args.get("tags", ALL_TAGS_NAME))
    not_tags = prepareFilterArg(request.args.get("not-tags", "null"))
    add_reg_names = prepareFilterArg(request.args.get("add-reg-names", "null"))
    add_regs_str = prepareFilterArg(request.args.get("add-regs", "null"))
    expand = request.args.get("expand-addresses", "true")
    dataset_cols = prepareFilterArg(request.args.get("fields", "null"))

    dataset_cols = map(
        lambda x: "access" if x == "rw" else x,
        dataset_cols
    )

    # If the desired attributes were not provided, use defaults.
    if not dataset_cols:
        dataset_cols = serialize.DEVICE_MODBUS_MAP_COLS

    # Check if a device was specified and, if it wasn"t, default to all devices.
    if device_name in INVALID_FILTER_ARGUMENTS:
        device_name = ALL_DEVICES_NAME

    # If not specified, do not expand LMMM fields.
    if expand in INVALID_FILTER_ARGUMENTS:
        expand = "false"

    # Choose between either the MODBUS maps with raw LJMMM entries or the maps
    # with LJMMM fields interpreted and expanded.
    if expand == "true" or add_regs_str:
        regs_to_use = reg_data_expanded
    else:
        regs_to_use = reg_data_compressed

    # Filter out which entries to use based on device.
    if device_name != ALL_DEVICES_NAME:
        regs_to_use = [x for x in regs_to_use if match_device(x, device_name)]

    # If the selected device / modbus map is not available, default to not
    # found.
    if len(regs_to_use) == 0:
        flask.abort(404)

    # Pre filter
    unfiltered_registers = []
    if add_reg_names:
        for entry in regs_to_use:
            for reg_num in add_reg_names:
                if unicode(reg_num) in unicode(entry["name"]):
                    unfiltered_registers.append(entry)

    if add_regs_str:
        add_regs = map(lambda x: int(x), add_regs_str)
        regs_to_use = filter(lambda x: x["address"] in add_regs, regs_to_use)

    # Filter by tag
    if tags and unicode(ALL_TAGS_NAME) not in tags:
        tags_set = set(tags)
        regs_to_use = filter(
            lambda x: set(x["tags"]).issuperset(tags_set),
            regs_to_use
        )

    # Filter by not-tag
    if not_tags: # and unicode(NO_TAGS_NAME) not in not_tags:
        entries_to_remove = []
        for entry in regs_to_use:
            for map_tag in entry["tags"]:
                for not_tag in not_tags:
                    if map_tag.find(unicode(not_tag)) != -1:
                        entries_to_remove.append(entry)

        for entry in entries_to_remove:
            regs_to_use.remove(entry)

    # Add the pre-filter contents
    for unfiltered_reg in unfiltered_registers:
        duplicate = False
        for reg in regs_to_use:
            if unicode(unfiltered_reg["name"]) == unicode(reg["name"]):
                duplicate = True

        if not duplicate:
            regs_to_use.append(unfiltered_reg)

    # Serialize the results and return.
    modbus_map_serialized = serialize.serialize_device_modbus_map(regs_to_use,
        dataset_cols)
    response = flask.make_response(json.dumps(modbus_map_serialized))
    response.headers["X-XSS-Protection"] = "0"
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_REDISPLAY_DOMAIN
    return response


@app.route("/scribe", methods=["GET", "POST"])
def inject_data():
    """Controls to Inject data about register records into an HTML template.
    
    @return: HTML form through which the HTML template can be filled and
        rendered.
    @rtype: str or flask response (redirect)
    """
    if flask.request.method == "GET":
        return flask.render_template("inject_data.html")

    target_code = flask.request.form.get("input", "")
    return render_scribe(target_code)



@app.route("/scribe_component", methods=["GET"])
def inject_data_service():
    target_code = flask.request.args.get("input", "")
    return render_scribe(target_code)


def render_scribe(target_code):
    names = parse_ljsl.find_names(target_code)

    not_found_reg_names = []
    tag_class_tuples = lj_scribe.find_classes_from_map(
        names,
        reg_maps,
        not_found_reg_names
    )

    tag_subtags_by_class = lj_scribe.fia_organize_tag_by_class(tag_class_tuples)

    target_code = lj_scribe.fix_not_found_reg_names(
        target_code,
        not_found_reg_names
    )

    original_names = map(lj_scribe.find_original_tag_str, names)

    summaries = map(
        lambda x: lj_scribe.render_tag_summary(*x),
        zip(tag_subtags_by_class, names, original_names)
    )

    original_names_to_summaries = zip(original_names, summaries)

    for (original_name, summary) in original_names_to_summaries:
        target_code = target_code.replace(original_name, summary)

    prefix = flask.render_template("scribe_prefix.html")
    postfix = flask.render_template("scribe_postfix.html")
    return prefix + target_code + postfix


def uniques(seq, id_fun=None):
    """Remove duplicates from a collection.
    
    @param seq: The sequence to remove duplicates from.
    @type seq: iterable
    @keyword id_fun: The function to use to create a unique comparable identity
        for an element in the provided sequence. This is effectively a hashing
        function for elements of seq. Defaults to using the element itself as
        the hash.
    @type id_fun: function
    @author: http://www.peterbe.com/plog/uniqifiers-benchmark
    """
    # order preserving
    if id_fun is None:
        def id_fun(x): x
    seen = {}
    result = []
    for item in seq:
        marker = id_fun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result
    return result


@app.route("/error_scribe", methods=["GET", "POST"])
def inject_errors():
    if flask.request.method == "GET":
        return flask.render_template("inject_error.html")
    
    target_code = flask.request.form.get("input", "")
    error_string = "@"
    target_code =  target_code.replace('@error(', '')
    target_code =  target_code.replace(')', '')
    return render_error_scribe(target_code)
   
    
@app.route("/error_scribe_component", methods=["GET", "POST"])
def error_scribe():
    target_code = flask.request.args.get("input", "")
    return render_error_scribe(target_code)

def render_error_scribe(target_code):
    
    target_code = target_code.lower()
    if(target_code != ""):
        if(target_code == "all"):
            high = float("inf")
            low = high*-1
        else:
            error_range = target_code.split(',')
            low = int(error_range[0])
            high = int(error_range[1])
    else:
        high = float("inf")
        low = high*-1
    return format_errors(high,low)
   
    
def format_errors(high,low):
    raw_error = zip(ljmmm.get_errors())
    #sort errors based on high and low values
    output_dict = [x for x in raw_error if x[0]['error'] >= low and x[0]['error'] <= high] 
    #send filterd json to tag_summary_template_error.html for rendering
    return flask.render_template("tag_summary_template_error.html",tag =  output_dict)


if __name__ == "__main__":
    app.debug = True
    app.run(host=os.environ["IP"], port=int(os.environ["PORT"]))
    
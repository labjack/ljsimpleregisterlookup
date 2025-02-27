import json
import os


import flask
from flask import request
# from markupsafe import Markup

from ljm_constants import ljmmm


def format_errors(high, low):
    raw_error = list(zip(ljmmm.get_errors()))
    #sort errors based on high and low values
    output_dict = find_error_range_from_errors(low, high, raw_error)
    #send filtered json to tag_summary_template_error.html for rendering
    for x in range(0,len(output_dict)):
        data = json.loads(json.dumps(output_dict[x][0]))
        if "description" in data:
            data["description"] = ljmmm.apply_anchors(data["description"])
        output_dict[x] = data
    return flask.render_template("tag_summary_template_error.html", tag =  output_dict)


def find_error_range_from_errors(low, high, raw_error):
	return [x for x in raw_error if x[0]['error'] >= low and x[0]['error'] <= high] 

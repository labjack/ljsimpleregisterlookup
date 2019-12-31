from ljm_constants import ljmmm
import json

DEFAULT_JSON = ljmmm.get_registers_data(expand_names=True, inc_orig=True)


def get_formatted_modbus_data(raw_registers=DEFAULT_JSON):
	"""Convert json data into formated json Modbus data for the Modbus map. 
	
	Creates markup snippets and inserts them into the JSON data.
	See lj_modbus_tests.py for example input and output 

	@keyword raw_registers: essentially the JSON object from ljmmm get_registers_data
	@type raw_registers: List
	@return: JSON obj that is marked up and ready for insertion into the template 
	@rtype: List
	"""
	tag_mappings = ljmmm.get_tag_mappings()
	formatted_output = []
	for k in range(len(raw_registers)):
		list_of_names = []
		extra_data = ""
		description = ""

		if len(raw_registers[k][1]) > 1: #map expanded registers to main register
			for t in range(len(raw_registers[k][1])):
				base = raw_registers[k][0]
				name = raw_registers[k][1][t]['name']
				address = raw_registers[k][1][t]['address']
				list_of_names.append({'name':name, 'address':address})
			raw_registers[k][0]['list_of_names'] = list_of_names

		if 'tags' in raw_registers[k][0]: #map tags to tags from tag_mappings in ljm_constants
			tags = ""
			for j in raw_registers[k][0]['tags']:
				if j in tag_mappings:
					tags += '<a href="https://labjack.com' + tag_mappings[j] + '" target="_blank">' + j+ '</a>, '
				else:
					tags += j + ", "
			raw_registers[k][0]['tags'] = tags[:-2]

		if 'description' in raw_registers[k][0]: #add description to sub details
			description = raw_registers[k][0]['description']
		else:
			description = "No Description"

		if 'default' in raw_registers[k][0]: #add default value to sub details
			if raw_registers[k][0]['default'] != 0:
				extra_data += '&nbsp; &#8226; Default value: ' + str(raw_registers[k][0]['default'])+'<br/>'

		if 'streamable' in raw_registers[k][0]:  #add streamable to sub details
			if raw_registers[k][0]['streamable']:
				extra_data += "&nbsp; &#8226; This register may be <a href='https://labjack.com/support/datasheets/t-series/communication/stream-mode' target='_blank'>streamed</a><br/>" 

		if 'isBuffer' in raw_registers[k][0]: #add isBuffer to sub details
			if raw_registers[k][0]['isBuffer']:
				extra_data += "&nbsp; &#8226; This register is a <a href='https://labjack.com/support/datasheets/t7/communication/modbus-map/buffer-registers'>Buffer Register</a><br/>"

		if 'usesRAM' in raw_registers[k][0]:  #add usesRAM to sub details
				if raw_registers[k][0]['usesRAM']:
					extra_data += "&nbsp; &#8226; This register uses system RAM. The maximum RAM is 64KB. For more information, see <a href='/support/datasheets/t-series/hardware-overview/ram'>4.4 RAM</a></li><br/>"

		if 'constants' in raw_registers[k][0]: #add constants table value to sub details
			extra_data += "<table class='sub-details'><thead><tr><td>Constant</td><td>Value</td></tr></thead><tbody>"
			for m in raw_registers[k][0]['constants']:
				value = m['value']
				name = m['name']
				extra_data += "<tr><td>" + name + "</td><td>" + str(value) + "</td></tr>"
			extra_data += "</tbody></table>"

		if 'devices' in raw_registers[k][0]:	#add device specfic data to sub details
			device = ""
			for m in raw_registers[k][0]['devices']:
				T7 = ""
				T4 = ""
				if 'device' in m:
					if m['device'] == 'T7':
						device += 'T7'
						if 'description' in m:
							T7 += '&nbsp;&nbsp;&nbsp;&nbsp; -' + m['description'] + '<br/>'
						if 'fwmin' in m:
							T7 += "&nbsp;&nbsp;&nbsp;&nbsp; -Minimum <a href='https://labjack.com/support/firmware'>firmware</a> version: " + str(m['fwmin']) + "<br/>"
						if len(T7)> 0:
							extra_data += '&nbsp; &#8226; T7-specific:</br>' + T7
					elif m['device'] == 'T4':
						device += 'T4'
						if 'description' in m:
							T4 += '&nbsp;&nbsp;&nbsp;&nbsp; -' + m['description'] + '<br/>'
						if 'fwmin' in m:
							T4 += "&nbsp;&nbsp;&nbsp;&nbsp; -Minimum <a href='https://labjack.com/support/firmware'>firmware</a> version: " + str(m['fwmin']) + "<br/>"
						if len(T4)> 0:
							extra_data += '&nbsp; &#8226; T4-specific:</br>' + T4
					elif m['device'] == 'DIGIT':
						device += 'DIGIT'
						extra_data += "&nbsp; &#8226; DIGIT-specific:</br> &nbsp;&nbsp;&nbsp;&nbsp; -Minimum <a href='https://labjack.com/support/firmware'>firmware</a> version: " + str(m['fwmin']) + "<br/>"
				else:
					device += m
			raw_registers[k][0]['devices'] = device

		if 'list_of_names' in raw_registers[k][0]: # adds expanded names to sub details
			expand_names = ""
			expand_names_show = ""
			expand_address = ""
			expand_address_show = ""
			expand_id= raw_registers[k][0]["address"]
			table_header = "<br/><table class='sub-details'><thead><tr><td>Expanded Names</td><td>Address</td></tr></thead><tbody>"
			for m in range(len(raw_registers[k][0]['list_of_names'])):
				address = raw_registers[k][0]['list_of_names'][m]['address']
				name = raw_registers[k][0]['list_of_names'][m]['name']
				
				if m < 3:
					expand_names_show +=  name + ", "
					expand_address_show +=  str(address) + ", "
				elif(m == 3):
					table_header = "<br/><table class='sub-details'><thead><tr><td>Expanded Names &nbsp;<a onclick='showHidden(" + str(expand_id)+ ")'" + " href='#' id='show" + str(expand_id)+ "' style='display: inline;'><img src='https://ljsimpleregisterlookup.herokuapp.com/static/images/closed_gray.png' id='show" + str(expand_id)+ "img' alt='Show all' height='15' width='15'></a></td><td>Address  &nbsp;<a onclick='showHidden(" + str(expand_id)+ ")'" + " href='#' id='show1" + str(expand_id)+ "' style='display: inline;'><img src='https://ljsimpleregisterlookup.herokuapp.com/static/images/closed_gray.png' id='show" + str(expand_id)+ "img1' alt='Show all' height='15' width='15'></a></td></tr></thead><tbody>"
					expand_names += "<span class='content-hide'  style='display: none;' id='" + str(expand_id)+ "'>" + name + ", "
					expand_address += "<span class='content-hide' style='display: none;' id='" + str(expand_id)+ "1'>" + str(address) + ", "
				else:
					expand_names +=  name + ", "
					expand_address +=  str(address) + ", "
			expand_names_show += expand_names
			expand_address_show += expand_address
			extra_data += table_header
			extra_data +=  "<tr><td>" + expand_names_show[:-2] + "</span></td><td>"+ expand_address_show[:-2]+ "</span></td></tr> </tbody></table>"

		raw_registers[k][0]['details'] = "<div class='expand-details'> Name: " + raw_registers[k][0]["name"] + "<br/>Description: "+ description + " <br/> " + extra_data + "</div> " #"+ raw_registers[k][0]['description'] + "
		formatted_output.append(raw_registers[k][0])
	return formatted_output

FORMATTED_OUTPUT = get_formatted_modbus_data()


def rendered_modbus_data():
	return FORMATTED_OUTPUT
	

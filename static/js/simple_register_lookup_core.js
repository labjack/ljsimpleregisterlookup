var LOOKUP = "/lookup.json?"

var host = window.location.host;
var BASE_URL;

deployed = host.indexOf("0.0.0.0") == -1;
deployed = deployed && host.indexOf("127.0.0.1") == -1;
deployed = deployed && host.indexOf("localhost") == -1;
deployed = deployed && host.indexOf("c9") == -1;
if (deployed) {
    BASE_URL = "https://ljsimpleregisterlookup.herokuapp.com/";
} else {
    BASE_URL = '';
}


var DEPLOY_URL = BASE_URL + LOOKUP;
var LOCAL_TEST_URL = LOOKUP;

var CURRENT_APP_URL = DEPLOY_URL;

var TAG_MAPPINGS = {
    "AIN":            "/support/datasheets/t-series/ain",
    "AIN_EF":         "/support/datasheets/t-series/ain/extended-features",
    "ASYNCH":         "/support/datasheets/t-series/digital-io/asynchronous-serial",
    "CONFIG":         "/support/datasheets/t-series/config",
    "DAC":            "/support/datasheets/t-series/dac",
    "DIO":            "/support/datasheets/t-series/digital-io/extended-features",
    "DIO_EF":         "/support/datasheets/t-series/digital-io/extended-features",
    "ETHERNET":       "/support/datasheets/t-series/ethernet",
    "FILE_IO":        "/support/datasheets/t-series/sd-card",
    "I2C":            "/support/datasheets/t-series/digital-io/i2c",
    "INTFLASH":       "/support/datasheets/t-series/internal-flash",
    "LUA":            "/support/datasheets/t-series/lua-scripting",
    "ONEWIRE":        "/support/datasheets/t-series/digital-io/1-wire",
    "RTC":            "/support/datasheets/t-series/rtc",
    "SBUS":           "/support/datasheets/t-series/digital-io/sbus",
    "SPI":            "/support/datasheets/t-series/digital-io/spi",
    "STREAM":         "/support/datasheets/t-series/communication/stream-mode",
    "TDAC":           "/support/datasheets/t-series/appendix-c-2",
    "UART":           "/support/datasheets/t-series/digital-io/asynchronous-serial",
    "USER_RAM":       "/support/datasheets/t-series/hardware-overview/ram",
    "WATCHDOG":       "/support/datasheets/t-series/watchdog",
    "WIFI":           "/support/datasheets/t-series/wifi",
};
var anOpen = [];

function attachListeners(oTable, detailIndices, tableID)
{
    $(window).resize(function() {
        oTable.fnAdjustColumnSizing();
    });
    $("#" + tableID + " td.control").die("click");
    $("#" + tableID + " td.control").live("click", function () {
        var nTr = this.parentNode;

        var i = $.inArray( nTr, anOpen );

        if ( i === -1 )
        {
            $("img", this).attr( "src", BASE_URL + "/static/images/details_close.png" );
            var nDetailsRow = oTable.fnOpen( nTr, fnFormatDetails(oTable, nTr, detailIndices), "details" );

            // Add the zebra stripe coloring to the details row.
            nDetailsRow.className += nTr.className;

            $("div.innerDetails", nDetailsRow).slideDown();
            anOpen.push( nTr );
        }
        else
        {
            $("img", this).attr( "src", BASE_URL + "/static/images/details_open.png" );
            $("div.innerDetails", $(nTr).next()[0]).slideUp( function () {
                oTable.fnClose( nTr );
                anOpen.splice( i, 1 );
            } );
        }
    });
}
function linkTagsToDatasheet(data) {
  for (i = 0; i < data.length; i++) {
    var tagsToReplace = data[i][4].replace(" ","").split(",");
    var tagsData = ""
    for(t = 0; t < tagsToReplace.length; t++) { 
        if(typeof TAG_MAPPINGS[tagsToReplace[t]] !== "undefined"){
          tagsData += '<a href="https://labjack.com'+ TAG_MAPPINGS[tagsToReplace[t]] +'" target="_blank">' + tagsToReplace[t]+ '</a>, '
        }else{
          tagsData += tagsToReplace[t] + ", ";
        }
    }
    data[i][4] = tagsData.substring(0, tagsData.length - 2); 
 }
 return data;
}

/**
 * Updates the registers data table with the given registers data.
 *
 * Re-initalizes the registers data table with server-provided registers data,
 * hiding the loading indiciator and showing the table in the process.
 *
 * @param {array} data Registers 2D array provided by the server.
**/
var updateRegistersTable = function(data, tableContainer)
{
    var tableID = tableContainer + "-table";

    // Create bare table
    var resultHTML = "<table cellpadding=\"0\" cellspacing=\"0\" border=\"0\"" +
    "class=\"display registerTable\" id=\"" + tableID + "\"></table>";
    $("#" + tableContainer).html(resultHTML);

    var columnNames = data[0]; // Header

    var detailIndices = {
      "description": columnNames.indexOf("description"),
      "default": columnNames.indexOf("default"),
      "streamable": columnNames.indexOf("streamable"),
      "usesRAM": columnNames.indexOf("usesRAM"),
      "isBuffer": columnNames.indexOf("isBuffer"),
      "constants": columnNames.indexOf("constants"),
      "devices": columnNames.indexOf("devices"),
      "altnames": columnNames.indexOf("altnames"),
    };

    for (var detail in detailIndices) {
      var currentIndex = columnNames.indexOf(detail);
      if (currentIndex !== -1) {
        columnNames.splice(currentIndex, 1);
      }
    }

    var nameIndex = columnNames.indexOf("name");

    // Generate columns
    var columns = columnNames.map(function(x) {
        return { "sTitle": x, "sClass": "left", "sWidth": "90px"};
    });

    columns[nameIndex].sWidth = "40px";

    // Add description column controls
    columns.push(
        {
            "sTitle": "details",
            "mDataProp": null,
            "sClass": "control center",
            "mRender": function(x) {
                var retCode = "<img src=\"";
                retCode += BASE_URL;
                retCode += "/static/images/details_open.png\">";
                return retCode;
            },
        }
    );

    // Remove header
    var headerlessData = data.slice(1);

    // Initialize data table
    var oTable = $("#" + tableContainer + "-table").dataTable( {
        "aaData": headerlessData,
        "aoColumns": columns,
        "aaSorting": [[ 1, "asc" ]],
        "bJQueryUI": true,
        "sPaginationType": "full_numbers",
        "bAutoWidth": false
    } );

    // http://datatables.net/forums/discussion/3835/width-columns-problem-in-chrome-safari/p1
    setTimeout( function () {
        oTable.fnAdjustColumnSizing();
    }, 10 );

    // Attach details link listeners
    attachListeners(oTable, detailIndices, tableID);

    // Show table
    $("#" + tableContainer).show();

}

function display_constants() {
  if (!this.constants || !this.constants.length || this.constants.length === 0) {
    return '';
  }
  var constants_template = `
    <table class="sub-details">
    <thead>
      <tr>
        <td><strong>Constant</strong></td>
        <td><strong>Value</strong></td>
      </tr>
    </thead>
    <tbody>
    {{#constants}}
      <tr>
        <td>{{name}}</td>
        <td>{{value}}</td>
      </tr>
    {{/constants}}
    </tbody>
    </table>
  `;
  return Mustache.render(constants_template, this);
}

function fnFormatDetails( oTable, nTr, detailIndices)
{
  var aData = oTable.fnGetData( nTr );
  var view = {
    "description": aData[detailIndices["description"]],
    "device_description": function() {
      // Prevent it from looking up the scope and finding the non-device "description"
      if (this.description)
        return this.description;
      return '';
    },
    "display_fwmin": function() {
        if (this.fwmin.toFixed) {
            return this.fwmin.toFixed(4);
        }

        // Because superstitious
        return this.fwmin;
    }
  };
  if (aData[detailIndices["default"]] !== null && aData[detailIndices["default"]] !== undefined) {
    view["default"] = aData[detailIndices["default"]].toString();
  }
  if (aData[detailIndices["streamable"]]) {
    view["streamable"] = true;
  }
  if (aData[detailIndices["usesRAM"]]) {
    view["usesRAM"] = true;
  }
  if (aData[detailIndices["isBuffer"]]) {
    view["isBuffer"] = true;
  }
  if (aData[detailIndices["constants"]]) {
    view["display_constants"] = display_constants;
    view["constants"] = aData[detailIndices["constants"]];
  }

  if (aData[detailIndices["altnames"]]) {
    view["altnames"] = aData[detailIndices["altnames"]];
  }

  var devs = aData[detailIndices["devices"]];
  if (devs) {
    for (dev in devs) {
      if (
        devs[dev]["fwmin"] != 0 ||
        devs[dev]["description"] ||
        devs[dev]["default"]
      ) {
        view["devices"] = devs;
        break;
      }
    }
  }

  var template = `
<div class="innerDetails">
{{{description}}}
<ul>
{{#altnames}}
  <li>Also known as: {{.}}</li>
{{/altnames}}
</ul>
<ul class="additional-details">
  {{#default}}
    <li>Default: {{default}}</li>
  {{/default}}
  {{#streamable}}
    <li>This register may be streamed</li>
  {{/streamable}}
  {{#usesRAM}}
    <li>This register uses system RAM. The maximum RAM is 64KB. For more information, see <a href="https://support.labjack.com/docs/4-0-hardware-overview-t-series-datasheet#id-4.0HardwareOverview%5BT-SeriesDatasheet%5D-RAM" target="_top">4.4 RAM</a></li>
  {{/usesRAM}}
  {{#isBuffer}}
    <li>This register is a <em><a href="https://support.labjack.com/docs/3-1-modbus-map-t-series-datasheet#id-3.1ModbusMap%5BT-SeriesDatasheet%5D-BufferRegisters" target="_top">buffer register</a></em></li>
  {{/isBuffer}}
  {{#devices}}
    <li>{{device}}-specific:
      <ul>
        {{#device_description}}
          <li>{{device_description}}</li>
        {{/device_description}}
        {{#fwmin}}
          <li>Minimum <a href="https://labjack.com/support/firmware" target="_top">firmware</a> version: {{display_fwmin}}</li>
        {{/fwmin}}
      </ul>
    </li>
  {{/devices}}
</ul>
  {{{display_constants}}}
</div>
`;
  return Mustache.render(template, view);
}

function RegistersTableRequester()
{
    var device = null;
    var tags = null;
    var notTags = null;
    var regNames = null;
    var regAddrs = null;
    var expand = null;
    var includeCSS = true;
    var fields = null;

    this.setDevice = function(newVal)
    {
        device = newVal;
    }

    this.setTags = function(newVal)
    {
        if(newVal instanceof Array)
            newVal = newVal.join(",");
        tags = newVal;
    }

    this.setNotTags = function(newVal)
    {
        notTags = newVal;
    }

    this.setRegNames = function(newVal)
    {
        if(newVal instanceof Array)
            newVal = newVal.join(",");
        regNames = newVal;
    }

    this.setRegAddrs = function(newVal)
    {
        if(newVal instanceof Array)
            newVal = newVal.join(",");
        regAddrs = newVal;
    }

    this.setExpand = function(newVal)
    {
        expand = newVal;
    }

    this.setFields = function(newVal)
    {
        fields = newVal;
    }

    this.loadTable = function(tableContainer, callback)
    {
        var data = {};

        if(device != null)
            data["device_name"] = device;
        if(tags != null)
            data["tags"] = tags;
        if(notTags != null)
            data["not-tags"] = notTags;
        if(regNames != null)
            data["add-reg-names"] = regNames;
        if(regAddrs != null)
            data["add-regs"] = regAddrs;
        if(expand != null)
            data["expand-addresses"] = expand;
        if(fields != null)
            data["fields"] = fields;

        $.getJSON(
            CURRENT_APP_URL,
            data,
            function(data) {
                data = linkTagsToDatasheet(data);
                updateRegistersTable(data, tableContainer); 
                callback();
            }
        );
    }

}

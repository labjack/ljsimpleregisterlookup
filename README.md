# LJSimpleRegisterLookup

LJSimpleRegisterLookup provides a web-based GUI for our device MODBUS
maps.\
LJSimpleRegisterLookup is released under the GNU GPL v2 license.

## Deploying

To deploy new [ljm_constants.json](https://github.com/labjack/ljm_constants/blob/master/LabJack/LJM/ljm_constants.json) changes:

To deploy changes to _ljm_constants_ using GitHub CI Actions
```sh
git clone ---recursive git@github.com:labjack/ljsimpleregisterlookup.git
cd ljsimpleregisterlookup
git checkout development
python3 -m venv venv                          # Create virtualenv venv
source venv/bin/activate                      # Activate venv
python3 -m pip install -r requirements.txt    # Install dependencies
cd ljm_constants
git checkout master                            # Sets the submodule ref to head of master
cd ../                                         # Go back to ljsimpleregisterlookup root
git status                                     # Make sure that the submodule was updated
python3 runtests.py                            # Make sure that all tests still pass
git add ljm_constants                          # Add the submodule to commit
git commit -m "Update ljm_constants submodule" # Reference the PR here if necessary
git push
```
After pushing, the GitHub Actions will run tests and then deploy to <http://ljsimpleregisterlookup-staging.herokuapp.com/>
you can view the status on the _Actions_ tab of the repo at <https://github.com/labjack/ljsimpleregisterlookup/actions>.
Once you verify that it has deployed correctly you can deploy it to production through either the Heroku dashboard 
or using the Action which deploys to production (by merging development into the main branch).

For more info on deploying _ljsimpleregisterlookup_ see the **Deployment** section below.



##### Old Way using Heroku CLI ()
- [Install](https://devcenter.heroku.com/articles/heroku-cli#download-and-install) and sign into the Heroku CLI
- Pull the new changes into ljsimpleregisterlookup
    (ljsimpleregisterlookup/ljm_constants is a git submodule)
- If the ljm_constants.json's `tag_mappings` have changed, update
    `TAG_MAPPINGS` in `static/js/simple_register_lookup_core.js`.
- Commit the change to ljsimpleregisterlookup


## Overview for the project (tl;dr)

**LJSimpleRegisterLookup**\
Simple Register Lookup provides a device drop-down menu that then
displays MODBUS maps in a searchable / paginated table. In addition to
this embeddable front-end, a programmatic API is also available using
simple HTTP GET requests on URLs following the pattern
<http://ljsimpleregisterlookup.herokuapp.com/lookup.json?device_name=T7>.
LabJack currently serves this tool at available at
<http://ljsimpleregisterlookup.herokuapp.com>.

**LJScribe**\
LJScribe generates HTML documentation for registers based on the JSON
modbus map. LabJack currently serves this tool at
<http://ljsimpleregisterlookup.herokuapp.com/scribe>.

**LJMMM / LJSL**\
This project implements Python parsers for both LabJack MODBUS Map
Markup and LabJack Scribe Language. The formal spec for LJMMM, the
markup that aids in the construction of the JSON MODBUS map, is
available at <http://jsfiddle.net/Q2F4V/embedded/result/> and an informal
discussion follows. LJSL, the language used with LJScribe, does not
currently have a formal spec but a brief discussion also follows.

## LJMMM

LabJack MODBUS Map Markup provides automatic enumeration of names and
registers in LabJack's JSON MODBUS map. While a formal spec is at
<http://jsfiddle.net/Q2F4V/embedded/result/>, LJMMM fields interprets both
special fields in register names as well as data types for the automatic
enumeration of addresses. The existing [JSON MODBUS
map](https://github.com/labjack/ljm_constants/blob/master/LabJack/LJM/ljm_constants.json)
already uses LJMMM extensively.

**Names**\
LJMMM names are interpreted as LMMM Field Language which should consist
of all caps with numbers and underscores. The pound sign indicates
enumeration as the four following examples demonstrate:

- TEST_AND_TESTING becomes TEST_AND_TESTING.
- AIN#(10:3:2) becomes the collection: AIN10, AIN12, AIN14.
- AIN#(5:3) becomes the collection: AIN5, AIN6, AIN7. This is
    equivalent to AIN#(5:3:1).
- TEST_poundTESTING becomes TEST#TESTING.

**Addresses**\
LJMMM specifies the available list of value data types that may extend
beyond a 2-byte MODBUS register and, thus, provides automatic
enumeration for addresses. Those valid datatypes include:

- FLOAT32
- UINT16
- UINT32
- UINT64
- INT16
- INT32
- INT64
- STRING

Please note that LJMMM attempts to standardize the other attributes of
JSON objects in the MODBUS map and, before editing that document, please
review the [short formal
spec](http://jsfiddle.net/Q2F4V/embedded/result/).

**Descriptions**\
LJMMM auto-processes substrings in the descriptions that look like URLs.
For these, it outputs external link anchor tags with extlink icons. If
the substring is <https://labjack.com/support/>, replaces it with output
like:

`<a target=\"_blank\" href=\"https://labjack.com/support/\">https://labjack.com/support/</a><img style="margin-right: -1;" src="https://ljsimpleregisterlookup.herokuapp.com/static/images/ui-icons-extlink.png" />`

## LJSL

[LJScribe](http://ljsimpleregisterlookup.herokuapp.com/scribe) reads
LabJack Scribe Language to produce HTML output. Basically Scribe looks
for `registers: or`registers(Title Text): followed by a comma separated
list of LJMMM Field Language entries. Currently scribe limits these
fields to a single enumeration. So, AIN#(1:10) is valid but
AIN#(1:10)\_#(1:10) is not currently supported. An example of input into
LJScribe is at <https://gist.github.com/Samnsparky/7122519> and the
corresponding output is at <http://jsfiddle.net/sampottinger/36vCD/>.
Notice that the styling in the jsfiddle is slightly different than how
it will appear on LabJack's pages due to inherited CSS rules.

## Technology used

The back-end is written in Flask (Python, <http://flask.pocoo.org/>) and
runs on Heroku (<http://www.heroku.com/>). The front-end uses jQuery
(<http://jquery.com/>), jQuery UI (<http://jqueryui.com/>), and DataTables
(<http://www.datatables.net/>). The current deployment uses Gunicorn
(<http://gunicorn.org/>) for its web server.

CI deployments are done using GitHub Actions.

## Development Standards

Any new development should be done in a feature branch off of *development*,
once tested and verified, it can then be merged back into *development*.

The *main* branch reflects the version currently deployed in production,  
and should only be merged with *development* when ready to deploy.

All Python documentation is written in epydoc
(<http://epydoc.sourceforge.net/>) and all JavaScript documentation is
written in jsdoc (<http://en.wikipedia.org/wiki/JSDoc>). The development
team has not set the precedent for client-side code testing but server
logic should be tested using the Python unittest module as appropriate
(<http://docs.python.org/2/library/unittest.html>). The application uses
the ljm_constants.json file in the
[LJM_constants](https://github.com/labjack/ljm_constants) repository.

## Development Environment Setup

The rest of this README concerns the development and modification of
LJSimpleRegisterLookup, LJScribe, and LJMMM / LJSL, a discussion more
suited for LabJack developers and not users of these solutions.

Requirements:

- Heroku account with Heroku toolbelt (<https://toolbelt.heroku.com/>).
- Get collaborator permissions on Heroku.
- Get collaborator permissions on GitHub.
- Allow Cross-Origin-Resource-Sharing (CORS) browser extension - "Allow CORS" or similar

Steps:

- Clone this repo (\$ git clone ---recursive
    git@github.com:labjack/ljsimpleregisterlookup.git)
- cd into directory
- setup virtualenv (venv) and install dependencies

Note that this repository has sub-modules and ---recursive or equivalent
is necessary during cloning.

## venv

LJSimpleRegister lookup uses venv
(<https://docs.python.org/3/library/venv.html>) and the gunicorn server.
Also, to accommodate cross-scripting security considerations, the
client-side JavaScript has a hard-coded URL.

To set up locally:

- \$ python3 -m venv venv
- \$ source venv/bin/activate
- \$ pip install -r requirements.txt

You can leave the virtual environment with `$ deactivate`.

## Automated Testing

All unit tests can be run with `$ python runtests.py`.

Any commits made to _development_ or _main_ branch will also trigger the unit tests.
See the results in the actions tab on GitHub.

## Local Development Server

A local web server can be run either through Flask or Gunicorn.
Gunicorn: (does not work on Windows)

- \$ gunicorn simple_register_lookup:app
- Navigate to 127.0.0.1:8000 or localhost:8000

Alternatively, Flask:

- Export IP = "127.0.0.1" and PORT = 3000 as ENV variables in your terminal
- \$ python simple_register_lookup.py
- Navigate to 127.0.0.1:3000 or localhost:3000

## Deployment

Deployment is handled mostly by GitHub CI/CD actions. After testing locally you can deploy to the staging environment by pushing or merging to the main branch. The action will run when commited and pushed, first running the unit tests, then deploying to <http://ljsimpleregisterlookup-staging.herokuapp.com/>.
Navigate there to see the deployed app. Make sure you have your CORS extension activated, it will not load the table otherwise. Also, make sure that the Heroku Web Dyno is turned on through the Heroku Dashboard, the page will not load, only a Heroku error page and a 503 HTTP Error Code.

Then, to deploy to production, log into the Heroku Dashboard, verify that staging has built and deployed correctly, and promote the staging environment to production.
Check the deployment succeeded on:

- The production deployed website
  - <http://ljsimpleregisterlookup-staging.herokuapp.com/>
- The embedded Modbus Map on our webite which pulls from prod (link may have changed)
  - <https://labjack.com/pages/support?doc=%2Fdatasheets%2Ft-series-datasheet%2F31-modbus-map-t-series-datasheet%2F>

If either shows an error, you can rollback to the previous deployment the Heroku Dashboard production project activity feed. This will prevent the service from being down while debugging the failed deployment.

## Common Tasks

**Update the Styling for Scribe Output**\
The CSS for LJScribe's output can be found in
/templates/scribe_prefix.html. Editing that file and redeploying will
change the CSS included with Scribe documentation output.

**Update the Scribe Template**\
The HTML template (written using [Jinja2](http://jinja.pocoo.org/docs/))
used for LJScribe's output can be found in
/templates/tag_summary_template.html. Editing that file and redeploying
will change the template used for rendering Scribe documentation output.

**Update the Scribe JavaScript Logic**\
Similarly, the JavaScript for LJScribe's output can be found in
/templates/scribe_postfix.html. Editing that file and redeploying will
change the JS included with Scribe documentation output.

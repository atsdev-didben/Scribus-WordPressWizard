# Scribus-WordPressWizard
Plugin for Scribus - enable import from a wordpress web site to a scribus page

Plugin Wordpress for Scribus

The aim of this script is to enable the import of some posts from a wordpress web site to a scribus page.
No copy/paste between website and scribus needed.

DESCRIPTION & USAGE

Once lauched, this plugin display a UI which offers the user to first fill the url of the desired wordpress web site.
Follow the steps hereafter in order to retrive the desired posts :

1. Fill the url source of the wordpress web site
2. Press the button retreive to catch all sections of the wordpress site.
3. select the section into the listbox of sections.
4. All related posts are displayed into the article listbox.
5. Select all posts you want and press the button Import
6. The plugin window will be closed after the import process, and the scribus page content will be updated.

N.B : this plugin is based on wordpress API v2

TO INSTALL : 

Just copy the WordPressWizard.py python script into the share/scripts folder of your scribus install.

Check the Python module dependencies :

* tempfile
* ByteIO
* html + HTMLParser
* requests

You could install all of these by PIP under the python embeded in scribus application

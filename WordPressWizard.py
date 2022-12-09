#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
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

AUTHOR:
    Didier Bénadet <d.benadet@atsdev.fr>

LICENSE:
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

"""

import sys

try:
    import requests
except ImportError:
    messageBox("REQUESTS","Unable to import the Python Requests module.",ICON_CRITICAL,BUTTON_OK)
    sys.exit(1)

try:
    import tempfile
except ImportError:
    messageBox("TEMPFILE","Unable to import the Python TEMPFILE module.",ICON_CRITICAL,BUTTON_OK)
    sys.exit(1)

try:
    import html
except ImportError:
    messageBox("HTML","Unable to import the Python HTML module.",ICON_CRITICAL,BUTTON_OK)
    sys.exit(1)

try:
    from html.parser import HTMLParser
except ImportError:
    messageBox("HTMLParser","Unable to import the Python HTMLParser module.",ICON_CRITICAL,BUTTON_OK)
    sys.exit(1)

try:
    from io import BytesIO
except ImportError:
    messageBox("BytesIO","Unable to import the Python BytesIO module.",ICON_CRITICAL,BUTTON_OK)
    sys.exit(1)

try:
    from scribus import *
except ImportError:
    print ("This Python script is written for the Scribus scripting interface.")
    print ("It can only be run from within Scribus.")
    sys.exit(1)

try:
    from tkinter import *
    from tkinter import font
except ImportError:
    print ("This script requires Python's Tkinter properly installed.")
    messageBox('Script failed',
               'This script requires Python\'s Tkinter properly installed.',
               ICON_CRITICAL)
    sys.exit(1)

try:
    from PIL import Image
except ImportError:
    messageBox("PIL","Unable to import the Python Imaging Library module.",ICON_CRITICAL,BUTTON_OK)
    sys.exit(1)

""" Setting of all globals parameters """
titre = ""
article = ""
texte = ""
imgcpt = 0
numpost = 1
listObj = []

class MyHTMLParser(HTMLParser):
    """ HTML parser class which is called by the import process (and import button)
        include tag and data parsing
    """


    def handle_starttag(self, tag, attrs):
         """ Tag parsing function which supply the following functions :
         - Extract embeded images and build the image boxes (store the image file into the user temporary folder of the operating system.
         - Add the link embeded to text block.
         """
         global texte
         global imgcpt
         global numpost
         global listObj
         for attr in attrs:
              if attr[0] == 'src':
                   print("Image source : ", attr[1])
                   response = requests.get(attr[1])
                   myFile = attr[1].split('/', -1)[-1]
                   img = Image.open(BytesIO(response.content))
                   img = img.save(tempfile.gettempdir()+'/'+myFile)
                   xpos = numpost * 10
                   ypos = (imgcpt * 45) + 105 + ((numpost-1) * 10)
                   imgcpt = imgcpt + 1
                   ImageFrame = createImage(xpos, ypos, 45, 45)
                   listObj.append(ImageFrame)
                   loadImage(tempfile.gettempdir()+'/'+myFile, ImageFrame)
                   setScaleImageToFrame(True, False,ImageFrame)
                   setFillColor("None", ImageFrame)
                   setLineColor("None", ImageFrame)
              if attr[0] == 'href':
                   texte = texte + "\r\n" + attr[1]


    def handle_data(self, data):
        """ Data parsing : build the content of the article text block
        """
        tag = self.get_starttag_text()
        global texte
        if tag is not None:
            if ("<p" in tag or tag == "<ul>" or tag == "<li>" or tag == "<h1>" or tag == "<h2>" or tag == "<h3>" or tag == "<br>"):
                   texte = texte + "\r\n" + html.unescape(data)
            if (tag == "<strong>" or tag == "<em>"):
                   texte = texte + html.unescape(data)



class TkWordPress(Frame):
    """ GUI interface for Scribus WordPress Wizard.
        all functions are embeded into the ui elements"""


    def __init__(self, master=None):
        master.title("WordPress to Scribus Wizard")
        master.rowconfigure(4, weight=1)
        master.columnconfigure(0, weight=1)
        master.columnconfigure(1, weight=1)
        def RubSelected(event):
             """ Function activated by a section selection
              the supplied features are :
              - retreive all posts from the selected section (max 100 posts)
              - fill a dictionnary with all posts and its titles.
              - fill a dictionnary with all featured images linked to the posts
              - fill the list box dedicated to the posts
             """
             widget = event.widget
             selection=widget.curselection()
             picked = widget.get(selection[0])
             #print(picked)
             req2 = requests.get(entryUrl.get()+"/wp-json/wp/v2/posts?categories="+str(dicrubriques[picked])+"&per_page=100")
             liste_articles = req2.json()
             index2 = 0
             listboxart.delete(0,listboxart.size())
             for article in liste_articles:
                  index2+=1
                  objtitle=article["title"]
                  objarticle=article["content"]
                  links=article["_links"]
                  featuredmedia = links["wp:featuredmedia"]
                  media0 = featuredmedia[0]
                  dicarticles[html.unescape(objtitle["rendered"])] = objarticle["rendered"]
                  dimedia[html.unescape(objtitle["rendered"])] = media0["href"]
                  listboxart.insert(index2, html.unescape(objtitle["rendered"]))
        
        
        def Urlfeaturedmedia(mediaurl):
             """ Function called to solve and find the url of the featured media of the selected post
              return the featured image url.
             """
             req = requests.get(mediaurl)
             mediajson = req.json()
             Urlmediarender = mediajson["guid"]
             Urlmedia = Urlmediarender["rendered"]
             return Urlmedia
        
        
        def ButRetreive():
              """ Function activated by the import retreive
              the supplied features are :
              - Retreive all sections (categories) of the filled site url (max 100)
              - fill the list box dedicated to the sections
              """
              listboxrub.delete(0,listboxrub.size())
              req = requests.get(entryUrl.get()+"/wp-json/wp/v2/categories?per_page=100&per_page=100")
              liste_rubriques = req.json()
              index=0
              for rubrique in liste_rubriques:
                    index+=1
                    dicrubriques[rubrique["name"]] = rubrique["id"]
                    listboxrub.insert(index,rubrique["name"])
        
        
        def ButImport():
             """ Function activated by the import button
              the supplied features are :
              for each posts selected in the article list box
              - Get the title
              - Get the text of the post by lauching the html parser (included images were builded by the html parser)
              - Get the featured image linked to the post
              - Set all boxes (title+text+image featured+images included into the post)
              - Group all boxes
              - Finally, refresh the scribus page and close the WordPressWizard window
             """
             global texte
             global listObj
             global numpost
             global imgcpt
             selection = listboxart.curselection()
             for post in selection:
                 titre = listboxart.get(post)
                 article = dicarticles[titre]
                 featuredmedia = Urlfeaturedmedia(dimedia[titre])
                 response = requests.get(featuredmedia)
                 myFile = featuredmedia.split('/', -1)[-1]
                 img = Image.open(BytesIO(response.content))
                 img = img.save(tempfile.gettempdir()+'/'+myFile)
                 listObj = []
                 imgcpt = 0
                 texte = ""
                 xpos = numpost * 10
                 ypos = numpost * 10
                 parser = MyHTMLParser()
                 parser.feed(article)
                 blockTitre = createText(xpos, ypos, 45, 10)
                 setTextAlignment(1,blockTitre)
                 setText(titre, blockTitre)
                 setFontSize(10, blockTitre)
                 setFontFeatures("bold", blockTitre)
                 blockTexte = createText(xpos, ypos + 10, 45, 40)
                 setTextAlignment(1,blockTexte)
                 setText(texte, blockTexte)
                 setFontSize(8, blockTexte)
                 ImageFrame = createImage(xpos, ypos + 50, 45, 45)
                 listObj.append(ImageFrame)
                 loadImage(tempfile.gettempdir()+'/'+myFile, ImageFrame)
                 setScaleImageToFrame(True, False,ImageFrame)
                 setFillColor("None", ImageFrame)
                 setLineColor("None", ImageFrame)
                 listObj.append(blockTitre)
                 listObj.append(blockTexte)
                 groupObjects(listObj)
                 numpost = numpost + 1
             scribus.docChanged(True)
             scribus.setRedraw(True)
             scribus.redrawAll()
             master.destroy()
         
         
        master.geometry("600x500")
        master.resizable(width=True, height=True)
        labelUrl = Label(master, text="Root Url WordPress Site", padx=5, pady=5)
        entryUrl = Entry(master)
        labelRub = Label(master, text="Sections List", padx=5, pady=5)
        labelArt = Label(master, text="Posts List", padx=5, pady=5)
        listboxart = Listbox(master, selectmode = "multiple")
        listboxrub = Listbox(master)
        dicrubriques = {}
        dicarticles = {}
        dimedia = {}
        buttonConnect = Button(master, text="Retrieve WordPress Site", padx=5, pady=5, command=ButRetreive)
        buttonImport = Button(master, text="Import WordPress Post", padx=5, pady=5, command=ButImport)
        labelUrl.grid(row = 0, column = 0, columnspan = 2, sticky="ew", padx=5, pady=5)
        entryUrl.grid(row = 1, column = 0, columnspan = 2, sticky="ew", padx=5, pady=5)
        buttonConnect.grid(row = 2, column = 0, columnspan = 2, sticky="ew", padx=5, pady=5)
        labelRub.grid(row = 3, column = 0, sticky="nsew", padx=5, pady=5)
        labelArt.grid(row = 3, column = 1, sticky="nsew", padx=5, pady=5)
        listboxrub.grid(row = 4, column = 0, sticky="nsew", padx=5, pady=5)
        listboxart.grid(row = 4, column = 1, sticky="nsew", padx=5, pady=5)
        buttonImport.grid(row = 5, column = 0, columnspan = 2, sticky="ew", padx=5, pady=5)
        listboxrub.bind('<<ListboxSelect>>', RubSelected)
        
        


def main():
    """ Application/Dialog loop with Scribus sauce around """
    try:
        statusMessage('Running script...')
        progressReset()
        fenetre = Tk()
        app = TkWordPress(fenetre)
        fenetre.mainloop()
    finally:
        if haveDoc() > 0:
            redrawAll()
        statusMessage('Done.')
        progressReset()


if __name__ == '__main__':
    if haveDoc() > 0:
        main()
    else:
        messageBox("WordPress Wizard", "You need to have a document open <i>before</i> you can run this script successfully.", ICON_INFORMATION)
import sys
import argparse
import shlex
import os
import http.client
import logging
import urllib.request
import urllib.parse
import json
from html.parser import HTMLParser
from pprint import pprint


DESC = 'Downloader to get D&D Map Assets from the TheTrove'


class TheTroveHTMLParser(HTMLParser):
    def __init__(self, args):
        super().__init__()
        self.tag_attr = {}
        self.site = args.site
        self.subdirectory = args.subdirectory
        if args.debugenum:
            self.download = False
        else:
            self.download = True

    def handle_tag_attr(self, tag, attr):
        logging.info("     attr: %s=%s" % (attr[0], attr[1]))
        self.tag_attr[attr[0]] = attr[1]
        
    def handle_starttag(self, tag, attrs):
        logging.info("Start tag: %s" % tag)
        self.tag_attr = {}
        for attr in attrs:
            self.handle_tag_attr(tag, attr)

    def handle_href_png(self, tag, value):
        if ("./" == value[0:2]):
            file = value[2:]
            folder = self.subdirectory + file
            url = "https://" + self.site + folder
        else:
            file = value
            folder = self.subdirectory + file
            url = "https://" + self.site + folder
            
        print ("Download PNG %s from url %s" % (file, url))
        if self.download:
            con = http.client.HTTPSConnection(self.site)
            con.request("GET", folder)
            reply = con.getresponse()
            logging.info("status %s, reason %s" % (reply.status, reply.reason))
            page = reply.read()
            con.close()
            print ("Writing %d bytes to %s" % (len(page), file))
            with open(file, "wb") as fd:
                fd.write(page)
        else:
            print ("Rehearsal enumeration, local file %s" % (file))

                
    def handle_endtag(self, tag):
        logging.info("End tag  : %s" % tag)
        if ("a" == tag):
            try:
                #print(self.tag_attr)
                #print("href = %s" % self.tag_attr["href"])
                if(-1 != self.tag_attr["href"].find(".png")):
                    self.handle_href_png(tag, self.tag_attr["href"])
            except KeyError as e:
                logging.debug("KeyError Exception = %s" % e)
                pass
            except IndexError as e:
                logging.debug("IndexError Exception = %s" % e)
                pass

    def handle_data(self, data):
        logging.info("Data     : %s" % data)

    def handle_comment(self, data):
        logging.info("Comment  : %s" % data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        logging.info("Named ent: %s" % c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        logging.info("Num ent  : %s" % c)

    def handle_decl(self, data):
        logging.info("Decl     : %s" % data)


# Downloads a page listing from the Trove and in turn downloads all the assets
def DownloadAsset(args):

    if None != args.verbosity:
        pprint(args)
        logging.getLogger().setLevel(args.verbosity)
    if args.debughttp:
        http.client.HTTPConnection.debuglevel = 1

    print("Listing remote %s at %s" % (args.subdirectory, args.site))
    conn = http.client.HTTPSConnection(args.site)
    conn.request("GET", args.subdirectory)
    reply = conn.getresponse()
    logging.info("status %s, reason %s" % (reply.status, reply.reason))
    page = reply.read()

    # download the following page, parse, and then download the contained files
    parser = TheTroveHTMLParser(args)
    parser.feed(page.decode("utf-8"))

    
# Downloads a predefined set of pages from the Trove into specific directories
def DownloadBatchAssets(args):
    
    arrSub = {}
    # local directory, remote path
    arrSub["Humans"] = "/Assets/Map%20Assets/Tokens/Humans/"
    arrSub["Undead"] = "/Assets/Map%20Assets/Tokens/undead/"
    arrSub["a0"] = "/Assets/Map%20Assets/Tokens/a0/"
    arrSub["a1"] = "/Assets/Map%20Assets/Tokens/a1/"
    arrSub["b0"] = "/Assets/Map%20Assets/Tokens/b0/"
    arrSub["c0"] = "/Assets/Map%20Assets/Tokens/c0/"
    arrSub["d0"] = "/Assets/Map%20Assets/Tokens/d0/"
    arrSub["d1"] = "/Assets/Map%20Assets/Tokens/d1/"
    arrSub["d2"] = "/Assets/Map%20Assets/Tokens/d2/"
    arrSub["d3"] = "/Assets/Map%20Assets/Tokens/d3/"
    arrSub["e0"] = "/Assets/Map%20Assets/Tokens/e0/"
    arrSub["f0"] = "/Assets/Map%20Assets/Tokens/f0/"
    arrSub["g0"] = "/Assets/Map%20Assets/Tokens/g0/"
    arrSub["g1"] = "/Assets/Map%20Assets/Tokens/g1/"
    arrSub["g2"] = "/Assets/Map%20Assets/Tokens/g2/"
    arrSub["h0"] = "/Assets/Map%20Assets/Tokens/h0/"
    arrSub["i0"] = "/Assets/Map%20Assets/Tokens/i0/"
    arrSub["l0"] = "/Assets/Map%20Assets/Tokens/l0/"
    arrSub["m0"] = "/Assets/Map%20Assets/Tokens/m0/"
    arrSub["n0"] = "/Assets/Map%20Assets/Tokens/n0/"
    arrSub["o0"] = "/Assets/Map%20Assets/Tokens/o0/"
    arrSub["p0"] = "/Assets/Map%20Assets/Tokens/p0/"
    arrSub["s0"] = "/Assets/Map%20Assets/Tokens/s0/"
    arrSub["s1"] = "/Assets/Map%20Assets/Tokens/s1/"
    arrSub["s2"] = "/Assets/Map%20Assets/Tokens/s2/" 
    arrSub["t0"] = "/Assets/Map%20Assets/Tokens/t0/"
    arrSub["v0"] = "/Assets/Map%20Assets/Tokens/v0/"
    arrSub["x0"] = "/Assets/Map%20Assets/Tokens/x0/"

    if None != args.verbosity:
        logging.getLogger().setLevel(args.verbosity)
    if args.debugenum:
        debugStr = "-E -V 30"
    else:
        debugStr = ""

    if (args.mkdirs):
        # create download directories, a two step processes
        for i in arrSub:
            os.mkdir(i)
    else:
        # download the remote files into the previously created directories
        for i in arrSub:
            try:
                os.chdir(i)
                os.system(r"..\..\TheTroveMapAssetsDownloader.py --subdirectory %s %s" % (arrSub[i], debugStr))
                os.chdir("../")
            except FileNotFoundError:
                print("Directory %s not found. Aborting. Create the download directories." % i)
                return



def main(argv):
    parser = argparse.ArgumentParser(description=DESC)

    verbosityChoices = [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING ]
    parser.add_argument('-V', '--verbosity', type=int, choices=verbosityChoices, help='increase output verbose level')
    parser.add_argument('-D', '--debughttp', action='store_true', help='turn on http debuging')
    parser.add_argument('-E', '--debugenum', action='store_true', help='enumerates files skipping the download')


    # https://thetrove.net/Assets/Map%20Assets/Tokens/Humans
    parser.add_argument('-f', '--subdirectory', type=str, default="/Assets/Map%20Assets/Tokens/Humans/", help='Trove Map Assets Subdirectory')
    # thetrove.net
    parser.add_argument('-s', '--site', type=str, default="thetrove.net", help='Trove Map Assets Subdirectory')

    # batch processing arguments
    parser.add_argument('-M', '--mkdirs', action='store_true', help='will create the download directories')
    parser.add_argument('-B', '--batchjob', action='store_true', help='will download predefined directories')

    args = parser.parse_args(argv[1:])

    if args.batchjob:
        DownloadBatchAssets(args)
    else:
        DownloadAsset(args)


if __name__ == "__main__":
    main(sys.argv)



    

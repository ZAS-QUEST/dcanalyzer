import sys
import time
import glob
import requests
import json
from collections import defaultdict
from lxml import etree
from lxml.html.soupparser import fromstring

def getIdentifiers(filename, typ):  
    tree = etree.parse(filename)
    etree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
    #retrieve all tags <dc:format>
    dcformats = tree.findall(".//{http://purl.org/dc/elements/1.1/}format")
    #retrieve all identifiers within a <oai_dc:dc> if there is reference to  file of given type
    for dcformat in dcformats: 
        if dcformat.text == typ: 
            identifiers = dcformat.findall("../{http://purl.org/dc/elements/1.1/}identifier")
            return identifiers
        
def retrieve(xmlfiles, mimetype): 
    #retrieve all identifiers found in the xml files which include relevant mimetype
    globalidentifiers = [getIdentifiers(x,mimetype) for x in xmlfiles]
    #remove empty return values
    records = [x for x in globalidentifiers if x != None]
    #flatten out tuples of multiple identifiers contained in one file 
    IDs = [x2.text for x in records for x2 in x] 
    print("found %i IDs (%i records) with references to %s files"%(len(IDs),len(records),mimetype))
    return IDs, records

def scan(d, xmlfiles, filetypes):
    print("Scanning %s" % d)    
    for filetype in filetypes:
        IDs, records = retrieve(xmlfiles,filetypes[filetype])
        
def download(xmlfiles, filetype):             
    elanIDs = retrieve(xmlfiles, filetypes[filetype])[0]
    #for interrupted downloads, set offset where to resume download 
    offset = 90
    print("offset is %s" %offset)
    for elanID in elanIDs[offset:]: 
        #check for validity of ID
        try:
            soasID = elanID.split("oai:soas.ac.uk:")[1]  
        except IndexError: #filename does not start with oai:soas.ac.uk:, so we are not interested
            continue
        #prepare request
        url = "https://elar.soas.ac.uk/Record/%s" % soasID
        phpsessid = ""
        cookie = {'PHPSESSID': phpsessid} 
        user, password = open('password').read().strip().split(',') #it is unclear whether we need user and pw; possibly the Session ID is sufficient
        payload = {'user':user, 'password':password}
        
        #retrieve catalog page
        print("retrieving %s" % url)
        with requests.Session() as s:
            r = s.post(url, cookies=cookie, data=payload)
            html = r.text
            #extract links to ELAN files
            try:
                links = fromstring(html).findall('.//tbody/tr/td/a')    
                eaflocations = list(set([a.attrib["href"] for a in links if a.attrib["href"].endswith('eaf')])) #make this configurable for other types
            except AttributeError:
                continue
            #dowload identified files
            for eaflocation in eaflocations:
                eafname = eaflocation.split('/')[-1] 
                print("  downloading %s:" %eafname, endchar = ' '), 
                eafname = "%s.eaf" % eafname[:200] #avoid overlong file names
                r2 = s.post(eaflocation, cookies=cookie, data=payload) 
                eafcontent = r2.text 
                with open("eafs/%s" % eafname,'w') as localeaf: 
                    localeaf.write(eafcontent)
                print("done")
        #give the server some time to recover
        time.sleep(4)
 
def olaceaf(xmlfile, typ): 
    tree = etree.parse(xmlfile)
    etree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
    globalidentifiers = []
    dico = defaultdict(list)
    #retrieve all tags <dc:format>
    dcformats = tree.findall(".//{http://purl.org/dc/elements/1.1/}format")
    #retrieve all identifiers within a <oai_dc:dc> if there is reference to  file of given type
    print(len(dcformats))
    for dcformat in dcformats:  
        if dcformat.text.strip() == typ:  
            identifiers = dcformat.getparent().findall(".//{http://purl.org/dc/elements/1.1/}identifier")            
            globalidentifiers.append(identifiers)
    records = [x for x in globalidentifiers if x != None]
    #flatten out tuples of multiple identifiers contained in one file 
    for IDs in records: 
        for item in IDs: #etree.findall returns list 
            dico[0].append(item.text.strip().replace("<","").replace(">",""))
    with open("olac.json", "w") as out:
        out.write(json.dumps(dico, sort_keys=True, indent=4))
    
if __name__ == "__main__":
    #d = sys.argv[1] #get directory to scan 
    ##get all xmlfiles in directory
    #xmlfiles = glob.glob("%s/*xml"%d) 
    
    #filetypes = {
        #"ELAN":"text/x-eaf+xml",
        #"Toolbox":"text/x-toolbox-text",
        #"transcriber":"text/x-trs",
        #"praat":"text/praat-textgrid",
        #"Flex":"FLEx"
        #}        
    
    ##scan(d,xmlfiles,filetypes)
    #download(xmlfiles,"ELAN")
    ids = olaceaf('ListRecords-20191115.xml', 'text/x-eaf+xml')
    
    
 

 


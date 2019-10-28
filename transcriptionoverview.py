import glob
from lxml import etree
import sys

def getIdentifiers(filename,typ): 
    tree = etree.parse(filename)
    etree.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
    #retrieve all tags <dc:format>
    dcformats = tree.findall(".//{http://purl.org/dc/elements/1.1/}format")
    #retrieve all identifiers within a <oai_dc:dc> if there is reference to an ELAN file
    for dcformat in dcformats: 
        if dcformat.text==typ: 
            identifiers = dcformat.findall("../{http://purl.org/dc/elements/1.1/}identifier")
            return identifiers

if __name__ == "__main__":
    d = sys.argv[1] #get directory to scan 
    #get all xmlfiles in directory
    xmlfiles = glob.glob("%s/*xml"%d) 
    
    #retrieve all identifiers found in the xml files which include ELAN files
    globalidentifiers = [getIdentifiers(x,"text/x-eaf+xml") for x in xmlfiles]
    #remove empty return values
    nonemptyglobalidentifiers = [x for x in globalidentifiers if x != None]
    #flatten out tuples of multiple identifiers contained in one file 
    flatlist = [x2.text for x in nonemptyglobalidentifiers for x2 in x]
    print("found %i IDs (%i records) with references to ELAN files in %s"%(len(flatlist),len(nonemptyglobalidentifiers),d))
    
     
    #retrieve all identifiers found in the xml files which include Toolbox files
    globalidentifiers = [getIdentifiers(x,"text/x-toolbox-text") for x in xmlfiles]
    #remove empty return values
    nonemptyglobalidentifiers = [x for x in globalidentifiers if x != None]
    #flatten out tuples of multiple identifiers contained in one file 
    flatlist = [x2.text for x in nonemptyglobalidentifiers for x2 in x]
    print("found %i IDs (%i records) with references to Toolbox files in %s"%(len(flatlist),len(nonemptyglobalidentifiers),d))
    
    #retrieve all identifiers found in the xml files which include transcriber files
    globalidentifiers = [getIdentifiers(x,"text/x-trs") for x in xmlfiles]
    #remove empty return values
    nonemptyglobalidentifiers = [x for x in globalidentifiers if x != None]
    #flatten out tuples of multiple identifiers contained in one file 
    flatlist = [x2.text for x in nonemptyglobalidentifiers for x2 in x]
    print("found %i IDs (%i records) with references to transcriber files in %s"%(len(flatlist),len(nonemptyglobalidentifiers),d))
    
    #retrieve all identifiers found in the xml files which include praat files
    globalidentifiers = [getIdentifiers(x,"text/praat-textgrid") for x in xmlfiles]
    #remove empty return values
    nonemptyglobalidentifiers = [x for x in globalidentifiers if x != None]
    #flatten out tuples of multiple identifiers contained in one file 
    flatlist = [x2.text for x in nonemptyglobalidentifiers for x2 in x]
    print("found %i IDs (%i records) with references to praat files in %s"%(len(flatlist),len(nonemptyglobalidentifiers),d))
     
    #retrieve all identifiers found in the xml files which include Flex files
    globalidentifiers = [getIdentifiers(x,"FLEx") for x in xmlfiles] #format is not proper MIME type
    #remove empty return values
    nonemptyglobalidentifiers = [x for x in globalidentifiers if x != None]
    #flatten out tuples of multiple identifiers contained in one file 
    flatlist = [x2.text for x in nonemptyglobalidentifiers for x2 in x]
    print("found %i IDs (%i records) with references to Flex files in %s"%(len(flatlist),len(nonemptyglobalidentifiers),d))
        
    
        

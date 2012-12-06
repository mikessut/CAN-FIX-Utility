#!/usr/bin/env python


import xml.dom.minidom

def _getText(node, element):
    """Retrieve the text from 'element' in DOM node"""
    elementNodes = node.getElementsByTagName(element)
    if elementNodes:
        s = ""
        for each in elementNodes[0].childNodes:
            if each.nodeType == each.TEXT_NODE:
                s = s + str(each.data)
        return s.rstrip()
    else:
        return None


def _getFloat(s):
    """Take string 's,' remove any commas and return a float"""
    if s:
        return float(s.replace(",",""))
    else:
        return None

        
def _getAuxData(node):
    """Retrieve the 'aux' data from the element 'node'
       Returns a list of the remarks or an empty list if there are none"""
    auxNodes = node.getElementsByTagName("aux")
    if auxNodes:
        auxList = ["" for each in range(15)]
        for each in auxNodes:
            s = ""
            index = int(each.getAttribute("id"))-1
            for child in each.childNodes:
                if child.nodeType == child.TEXT_NODE:
                    s = s + str(child.data)
                    
            auxList[index] = s
        return auxList
    else:
        return []
    
def _getRemarks(node):
    """Retrieve the 'remarks' elements from 'node'
       Returns a list of the remarks or an empty list if there are none"""
    remNodes = node.getElementsByTagName("remarks")
    remList = []
    if remNodes:
        for each in remNodes:
            s = ""
            for child in each.childNodes:
                if child.nodeType == child.TEXT_NODE:
                    s = s + str(child.data)
            remList.append(s)
    return remList

class CanFix:
    """Represent the CANFix protocol parameters.  It reads the xml file
       given as 'filename' and populates a list of groups and a dictionary
       of parameters.  The key to the parameters dictionary is the id as an integer"""
    def __init__(self, filename):
        self.groups = []
        self.parameters = {}
        
        doc = xml.dom.minidom.parse(filename)
        
        groupNodes = doc.getElementsByTagName("group")
        for each in groupNodes:
            self.groups.append({"name":_getText(each, "name"),
                                "startid":int(_getText(each, "startid")),
                                "endid":int(_getText(each,"endid"))})
        
        parameterNodes = doc.getElementsByTagName("parameter")
        for each in parameterNodes:
            id = int(_getText(each, "id"))
            self.parameters[id] = {"id":id,
                                   "name":_getText(each, "name"),
                                   "type":_getText(each, "type"),
                                   "units":_getText(each, "units"),
                                   "format":_getText(each, "format"),
                                   "count":int(_getText(each, "count")),
                                   "index":_getText(each, "index")}
            self.parameters[id]["multiplier"] = _getFloat(_getText(each, "multiplier"))
            self.parameters[id]["offset"] = _getFloat(_getText(each, "offset"))
            self.parameters[id]["min"] = _getFloat(_getText(each, "min"))
            self.parameters[id]["max"] = _getFloat(_getText(each, "max"))
            
            self.parameters[id]["auxdata"] = _getAuxData(each)
            self.parameters[id]["remarks"] = _getRemarks(each)
            

if __name__ == "__main__":
    canfix = CanFix("canfix.xml")
    print "Groups:"
    for each in canfix.groups:
        print " %s %d-%d" % (each["name"], each["startid"], each["endid"])
    
    print "Parameters:"
    for each in canfix.parameters:
        print str(each) + " - " + canfix.parameters[each]["name"]
        print "  ", canfix.parameters[each]["remarks"]
    

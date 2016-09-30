import re

import xml.etree.ElementTree as ET


NODE_PROPERTIES = 'properties'
NODE_PARAMS_DEF_MODEL = 'hudson.model.ParametersDefinitionProperty'
NODE_PARAMS_DEF = 'parameterDefinitions'
NODE_DEFAULT_VALUE = 'defaultValue'
NODE_NAME = 'name'

def processVars(manfiest, jenkinsVars={}):
    def resolver(m):
        varName = m.group(0)[1:]

        if not varName in jenkinsVars:
            raise RuntimeError('unresolved variable %r' % varName)

        return jenkinsVars[varName]

    r = re.compile(r"(\$[a-zA-Z0-9_]+)")

    return re.sub(r, resolver, manfiest)


def extractManifest(configFilePath, paramName,):
    tree = ET.parse(configFilePath)

    root = tree.getroot()

    props = root.find(NODE_PROPERTIES)
    if props == None:
        raise RuntimeError('could not find %r node' % NODE_PROPERTIES)


    model = props.find(NODE_PARAMS_DEF_MODEL)
    if model == None:
        raise RuntimeError('could not find %r node' % NODE_PARAMS_DEF_MODEL)

    paramDefs = model.find(NODE_PARAMS_DEF)
    if paramDefs == None:
        raise RuntimeError('could not find %r node' % NODE_PARAMS_DEF)

    for param in paramDefs:
        name = param.find(NODE_NAME)
        if name is None:
            raise RuntimeError('coud not find %r node' % NODE_NAME)

        if name.text == paramName:
            value = param.find(NODE_DEFAULT_VALUE)
            if value == None:
                raise RuntimeError('could not find %r node' % NODE_DEFAULT_VALUE)

            return value.text


    raise RuntimeError('could not find extract manifest')

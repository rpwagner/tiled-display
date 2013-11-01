import sys

def _DynamicImport(moduleName):
    mod = __import__(moduleName)
    components = moduleName.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    #return getattr(mod, className)
    return mod

def GetConfigLoadFunctions(path): # example: "configs.localTestConfig"
    # Convert file path to python path.

    """
    #   replace any "/" with "."
    path = path.replace("/", ".")
    """
    #   and if it ends with ".py", remove the ending.
    if path.endswith(".py"):
        path = path[:-3]

    print "Trying to import:", path
    try:
        prefixedPath = "configs." + path
        print "Trying to import:", prefixedPath
        c = _DynamicImport ( prefixedPath )
    except ImportError, e:
        try:
            c = _DynamicImport ( path )
        except ImportError, e:
            print e, dir(e), e.args
            print "Error: Unable to load config from either of these paths: ", prefixedPath, ",", path
            print "Make sure your config can be imported manually:\n    python -c \"import %s\"" % prefixedPath, 
            sys.exit()

    createFuncs = []
    # print dir(c)

    for i in dir(c):
        if i.startswith("Create") and "Config" in i:
            createFuncs.append(getattr(c,i))
        
    return createFuncs

def GetConfigLoadFunction(path): # example: "configs.localTestConfig"
    createFuncs = GetConfigLoadFunctions(path)
    if len(createFuncs) > 0:
        return createFuncs[0]
    else:
        return None

def LoadConfigPy(path):
    createConfigFunc = GetConfigLoadFunction(path)
    if callable(createConfigFunc):
        return createConfigFunc()
    else:
        print "Warning, function from LoadConfigPy is not callable)."
        return None

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        configPath = sys.argv[1]
    else:
        configPath = "configs.localTestConfig"

    CreateConfig = GetConfigLoadFunction(configPath)
    c = CreateConfig() 
    print "Loaded config", c.asDict()
    print
    print "Machines for this config:", c.getMachineHostnames()

    from socket import gethostname, getfqdn
    hostname = gethostname()
    print "Trying to get machineDescs for this hostname", hostname
    machineDescs = c.getMachineDescsByHostname(hostname)
    print machineDescs


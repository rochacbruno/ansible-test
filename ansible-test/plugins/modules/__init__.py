

def __getattr__(name):
    """
    This function is called whenever an attribute lookup has not found the
    attribute in the usual places (i.e. it is not an instance attribute nor is
    it found in the class tree for self).
    """
    # Create the module
    mod = __import__('plugins.modules.' + name, globals(), locals(), [name])
    # Return the attribute.
    return getattr(mod, name)

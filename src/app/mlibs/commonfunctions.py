def mbool(val):
    if isinstance(val,bool): return val
    elif isinstance(val,str): return val.lower() == 'true'
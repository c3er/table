garbage = (
    [['document.write(\'<table id="loading" cellpadding=0 cellspacing=0 \
border="0" align=right><tr><td><img \
src="http://images.asianbookie.com/loading.gif" width=16 height=16 border=0 \
valign=center align="left">',
        'Loading...']],
    [['.']]
)

def filter_garbage (tablelist):
    if type (tablelist) not in (list, tuple):
        raise ValueError ('tablelist must be a list or tuple')
    elif type (tablelist) == tuple:
        tablelist = list (tablelist)
    j = 0
    for i in range (len (tablelist)):
        if type (tablelist [j]) != Table:
            raise ValueError (
                'The elements of the tablelist must be all from type Table')
        if tablelist [j].data in garbage:
            tablelist.remove (tablelist [j])
        else:
            j += 1
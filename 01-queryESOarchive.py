import numpy as np
from astroquery.eso import Eso
from astropy.table import vstack
import pickle
import os
eso = Eso()
eso.ROW_LIMIT = -1

eso.login("alavail",store_password=True)

# First, list all SCIENCE polarimetry files taken in the date interval
# Time intervals are taken short, so that the max length of 10000files is not reached
stime = ['2009-01-01','2010-01-01','2011-01-01','2012-01-01','2013-01-01','2014-01-01','2015-01-01','2016-01-01','2017-01-01','2018-01-01','2019-01-01','2020-01-01',]
etime = ['2010-01-01','2011-01-01','2012-01-01','2013-01-01','2014-01-01','2015-01-01','2016-01-01','2017-01-01','2018-01-01','2019-01-01','2020-01-01','2021-01-01',]

def get_query_table(stime,etime):
    tableCir = eso.query_main(column_filters=  {
            'instrument': 'HARPS',
            'stime':stime, 
            'etime':etime,
            'dp_cat' : 'SCIENCE',
            'dp_tech' : 'ECHELLE,CIRPOL'
            }, 
        columns=['pi_coi','night', 'title', 'obs_name' ,'ob_id', 'tpl_start'],
        cache=False,
        help=False )
    tableCir.remove_column('DIMM Seeing at Start') # the format of this column change with time

    try:
        tableLin = eso.query_main(column_filters=  {
            'instrument': 'HARPS',
            'stime':stime, 
            'etime':etime,
            'dp_cat' : 'SCIENCE',
            'dp_tech' : 'ECHELLE,LINPOL'
            }, 
            columns=['pi_coi','night', 'title', 'obs_name' ,'ob_id', 'tpl_start'],
            cache=False,
            help=False )
        tableLin.remove_column('DIMM Seeing at Start') # the format of this column change with time
        table = vstack([tableCir,tableLin])
    except:
        table =tableCir
    # Sorting the data by observation time
    ii = np.argsort(table['MJD-OBS'])
    table = table[ii]
    return table

for i in range(len(stime)):
    buffer = get_query_table(stime[i],etime[i])
    if i == 0 : table = buffer
    else: table = vstack([table, buffer])
    print(i, len(buffer), len(table))

table.write('allobs.csv', overwrite=True)

uniqueTPLstart = np.unique(table['TPL START'])
goodTPLStartInd, goodTPLstart = np.array([],dtype=np.int32), np.array([],dtype=np.int32)
goodTPLStartEndInd = np.array([], dtype=np.int32)
for i in range(len(uniqueTPLstart)):
    ii = np.argwhere(table['TPL START'] == uniqueTPLstart[i])
    nobs = len(ii)
    if nobs % 4 == 0:
        goodTPLstart = np.append(goodTPLstart, uniqueTPLstart[i])
        goodTPLStartInd = np.append(goodTPLStartInd, np.int32( table[np.squeeze(ii[0])].index) )
        goodTPLStartEndInd = np.append(goodTPLStartEndInd, np.int32(table[np.squeeze(ii[0])].index+nobs) )

# Creating a table with all the "good" datasets : with 4*N exposures of the same TPL Start
for i in range(len(goodTPLstart)):
    buffer = table[goodTPLStartInd[i]:goodTPLStartEndInd[i]]
    if i==0: goodtable = buffer
    else: goodtable=vstack([goodtable,buffer])
goodtable.write('HARPSpol-good-datasets-all.csv',overwrite=True)

pickle.save(goodtable,open('HARPSpol-good-datasets-all.pickle','wb'))



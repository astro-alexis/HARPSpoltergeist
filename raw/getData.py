import numpy as np
from astroquery.eso import Eso
import os
eso = Eso()
eso.ROW_LIMIT = -1

eso.login("alavail",store_password=True)

# First, list all SCIENCE polarimetry files taken in the date interval
stime, etime = "2021-01-01", "2022-10-01"
table = eso.query_main(column_filters=  {
        'instrument': 'HARPS',
        'stime':stime, 
        'etime':etime,
        'dp_cat' : 'SCIENCE',
        'dp_tech' : 'ECHELLE,CIRPOL'
    }, 
    columns=['pi_coi','night', 'title', 'obs_name' ,'ob_id'],
    cache=False,
    help=False )

# Sorting the data by observation time
ii = np.argsort(table['MJD-OBS'])
table = table[ii]

# Get headers
h = eso.get_headers(table['Dataset ID'])

import numpy as np
from astroquery.eso import Eso
from astropy.table import vstack
import pickle
import os
eso = Eso()
eso.ROW_LIMIT = -1
eso.login("alavail",store_password=True)


table = pickle.load(open('HARPSpol-good-datasets-all.pickle','rb'))
uniqueTPLstart = np.unique(table['TPL START'])

for i in range(len(uniqueTPLstart)):
    ii = np.squeeze(np.argwhere(table['TPL START'] == uniqueTPLstart[-i]))
    h = eso.get_headers(table['Dataset ID'][ii])
    # safety check
    if len(ii) != h['HIERARCH ESO TPL NEXP'][0]: print('stranger danger')
    dir = 'data/science/'+str(h['HIERARCH ESO TPL START'][0])+'-'+str(h['OBJECT'][0])+'-'+str(h['HIERARCH ESO INS OPTI7 ID'][0])+'/'
    dir = dir.replace(' ','')
    try:
        os.mkdir(dir)
    except FileExistsError:
        continue

    datafiles = eso.retrieve_data(table['Dataset ID'][ii], destination=dir, unzip=False, continuation=True)
    print(dir)

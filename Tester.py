from operator import index
import shutil
from pandas.io.pytables import Term
import nimare
import os
import numpy as np
from nilearn import masking
import gc
import scipy
import csv
import nibabel as nib
from nilearn.image import resample_to_img
import pandas as pd
import zipfile

def Construct():
    if (os.path.exists('CSVData') == False):
        os.mkdir('CSVData')
    if (os.path.exists('TermMaps') == False):
        os.mkdir('TermMaps')
    if (os.path.exists('TermSets') == False):
        os.mkdir('TermSets')
    meta = meta = nimare.meta.cbma.mkda.MKDADensity()
    GradientList = []
    WordList = []
    threshold = 0.02
    maptype = 'stat'



    for idx, gs in enumerate(os.listdir('Gradients')):
        wordir = os.path.join("Gradients", gs)
        WordList.append(gs)
        if (idx == 0):
            mask = masking.compute_background_mask(wordir) 
        MaskedGradient = masking.apply_mask(wordir,mask)
        GradientList.append(MaskedGradient)
    GradientFrame = pd.DataFrame(GradientList, index=WordList, dtype='float16').T
    #GradientArray = np.asarray(GradientList, dtype='float16')


    SampleGradient = nib.load(wordir)


    print(GradientFrame)
    print(MaskedGradient.shape)
    FullList = []
    TermList = []

    for idx, ds in enumerate(os.listdir('Packaged_Datasets')):
        #if idx == 0:
         #   idx = idx + 4
        #    ds = "v5-topics-50.pkl"
        ns_dset = nimare.dataset.Dataset.load(os.path.join("Packaged_Datasets", ds))
        terms = ns_dset.get_labels()
        #all_ids = ns_dset.ids
        for tidx, i in enumerate(terms):
            Corrs = []
            term_dset = ns_dset.slice(ns_dset.get_studies_by_label(i))
            #if term_dset.shape[0] >= 1000:
                #term_dset = term_dset[0:1000]
            results = meta.fit(term_dset)
            results.save_maps(output_dir='TermMaps', prefix=i, prefix_sep='__')
            maskedResult = masking.apply_mask(resample_to_img(results.get_map(maptype), SampleGradient), mask)
            maskedSeries = pd.Series(maskedResult, dtype='float16')
            #maskedArray = np.asarray(maskedResult, dtype='float16')
            Corrs = GradientFrame.corrwith(maskedSeries).to_list()
            FullList.append(Corrs)
            TermList.append(i.split("__")[1])
            print("Completed ", i, ", correlation number ", tidx, "of ", len(terms), "in ", ds)
        with open(os.path.join('CSVData', '%s.csv'  % (ds.split(".")[0])), 'w') as f:
            writer = csv.writer(f)
            writer.writerows(zip(TermList, FullList))
        with zipfile.ZipFile('%s.zip' % (ds), 'w') as zipF:
            for file in os.listdir('TermMaps'):
                zipF.write(os.path.join("TermMaps/" + file), compress_type=zipfile.ZIP_DEFLATED)
        shutil.rmtree('TermMaps')
        os.mkdir('TermMaps')
        print(ds, " complete! Starting next one now...")

Construct()


from operator import index
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


def Construct():
    if (os.path.exists('CSVData') == False):
        os.mkdir('CSVData')
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
    #GradientFrame = pd.DataFrame(GradientList, index=WordList, dtype='float16').T
    GradientArray = np.asarray(GradientList, dtype='float16')


    SampleGradient = nib.load(wordir)


    print(GradientArray)
    print(MaskedGradient.shape)
    FullList = []
    TermList = []

    for idx, ds in enumerate(os.listdir('Packaged_Datasets')):
        if idx == 0:
            idx = idx + 3
            ds = "v5-topics-50.pkl"
        ns_dset = nimare.dataset.Dataset.load(os.path.join("Packaged_Datasets", ds))
        terms = ns_dset.get_labels()
        all_ids = ns_dset.ids
        for tidx, i in enumerate(terms):
            Corrs = []
            term_dset = ns_dset.slice(ns_dset.get_studies_by_label(i, label_threshold=threshold))
            results = meta.fit(term_dset)
            maskedResult = masking.apply_mask(resample_to_img(results.get_map(maptype), SampleGradient), mask)
            #maskedSeries = pd.Series(maskedResult, dtype='float16')
            maskedArray = np.asarray(maskedResult, dtype='float16')
            #Corrs = GradientFrame.corrwith(maskedSeries).to_list()
            for d in range(GradientArray.shape[0]):
                print("chung")
                Corr = scipy.stats.pearsonr(GradientArray[d], maskedArray)[0]
                Corrs = np.append(Corrs, Corr)
        
            FullList.append(Corrs)
            TermList.append(i.split("__")[1])
            print("Completed ", i, ", correlation number ", tidx, "of ", len(terms), "in ", ds)
        with open(os.path.join('%s.csv' % (ds)), 'w') as f:
            writer = csv.writer(f)
            writer.writerows(zip(TermList, FullList))
        print(ds, " complete! Starting next one now...")

Construct()


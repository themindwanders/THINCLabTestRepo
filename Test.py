from operator import index

from pandas.io.pytables import Term
import nimare
import os
import numpy as np
from nilearn import masking
import gc
import scipy
import nibabel as nib
from nilearn.image import resample_to_img
import pandas as pd
ns_dset = nimare.dataset.Dataset.load('Data/currentDatabase.pkl')
meta = meta = nimare.meta.cbma.mkda.MKDADensity()
terms = ns_dset.get_labels()
all_ids = ns_dset.ids
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

SampleGradient = nib.load(wordir)

print(GradientFrame)
print(ns_dset.annotations.shape)
print(MaskedGradient.shape)
FullList = []
TermList = []
for tidx, i in enumerate(terms):
    term_dset = ns_dset.slice(ns_dset.get_studies_by_label(i, label_threshold=threshold))
    results = meta.fit(term_dset)
    maskedResult = masking.apply_mask(resample_to_img(results.get_map(maptype), SampleGradient), mask)
    maskedSeries = pd.Series(maskedResult, dtype='float16')
    Corrs = GradientFrame.corrwith(maskedSeries).to_list()
    FullList.append(Corrs)
    TermList.append(i.split("__")[1])
    print("Completed ", i, ", correlation number ", tidx, "of ", len(terms))
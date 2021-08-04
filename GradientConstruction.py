

database = 'C:/Users/gooda/CondensedArr/VSCode/database.txt'
annotations = 'C:/Users/gooda/CondensedArr/analyses/'
annotationsnew2 = 'C:/Users/gooda/CondensedArr/analyses/v5-topics-400.txt'
outdir = 'C:/Users/gooda/CondensedArr/VSCode/'
outdir2 = 'C:/Users/gooda/CondensedArr/VSCode/database.pkl'
dataset = 'C:/Users/gooda/CondensedArr/VSCode/topicdset400.pkl'
Savedir = "C:\\Users\\gooda\\CondensedArr\\VSCode\\"
name = "topicarr"
datasetpath = 'C:/Users/gooda/CondensedArr/VSCode/database.pkl'
keypath = 'C:/Users/gooda/CondensedArr/keys/v5-topics-400.txt'

def Constructandsave(database, annotations, outdir):
    import os
    import nimare
    import requests
    import tarfile
    import gc
    if (os.path.exists('tempDir') == False):
        os.mkdir('tempDir')
    if (os.path.exists('Data') == False):
        os.mkdir('Data')
    if (os.path.exists('Gradients') == False):
        os.mkdir('Gradients')
    if (os.path.exists('Topics') == False):
        os.mkdir('Topics')

    url1 = "https://github.com/neurosynth/neurosynth-data/blob/master/current_data.tar.gz?raw=true"
    resp1 = requests.get(url1, stream=True)
    print(resp1.headers.get('content-type'))
    with open('tempDir/current_data', 'wb') as fd1:
        for chunk1 in resp1.iter_content(chunk_size=128):
            fd1.write(chunk1)
    tarfile.open('tempDir/current_data').extractall(path='tempDir')
    dbase = 'tempDir/database.txt'
    feats = 'tempDir/features.txt'
    ns_dset = nimare.io.convert_neurosynth_to_dataset(dbase,annotations_file=feats)
    ns_dset.save('Data/currentDatabase.pkl')
    gc.collect()
    os.remove('tempDir/database.txt')
    os.remove('tempDir/features.txt')
    os.remove('tempDir/current_data')

    url2 = "https://github.com/17iwgh/dbasepub/blob/main/GradRepo.tar?raw=true"
    resp2 = requests.get(url2, stream=True)
    with open('tempDir/Gradients', 'wb') as fd2:
        for chunk2 in resp2.iter_content(chunk_size=128):
            fd2.write(chunk2)
    tarfile.open('tempDir/Gradients').extractall(path='Gradients')
    gc.collect()
    os.remove('tempDir/Gradients')

    url3 = "https://github.com/neurosynth/neurosynth-data/blob/master/topics/v5-topics.tar.gz?raw=true"
    resp3 = requests.get(url3, stream=True)
    with open('tempDir/Topics', 'wb') as fd3:
        for chunk3 in resp3.iter_content(chunk_size=128):
            fd3.write(chunk3)
    tarfile.open('tempDir/Topics').extractall(path='Topics')
    gc.collect()
    os.remove('tempDir/Topics')
    







def CompareCorr(datasetpath, outdir, nameconv, threshold, chunksize):
    import nimare
    import numpy as np
    from nilearn import masking
    import gc
    import scipy
    import nibabel as nib
    from nilearn.image import resample_to_img
    ns_dset = nimare.dataset.Dataset.load(datasetpath)
    terms = ns_dset.get_labels()
    meta = nimare.meta.cbma.mkda.MKDADensity()
    I1 = nib.load(outdir + "CtmeF1.nii")
    I2 = nib.load(outdir + "CtmeF2.nii")
    I3 = nib.load(outdir + "CtmeF3.nii")
    mask = masking.compute_background_mask(I1)
    rge = int(len(terms)/chunksize)
    q=0
    for i in range(rge):
        Arrrrr = []
        MaskedData1 = masking.apply_mask([I1,I2,I3],mask)
        all_ids = ns_dset.ids
        termschunk = terms[(0+q):(chunksize+q)]
        all_idschunk = all_ids[(0+q):(chunksize+q)]
        for r in termschunk:
            term_dset = ns_dset.slice(ns_dset.get_studies_by_label(r, label_threshold=threshold))
            #notterm_dset = ns_dset.slice(sorted(list(set(all_idschunk) - set(ns_dset.get_studies_by_label(r, label_threshold=threshold)))))
            results = meta.fit(term_dset)
            term_name = (r.split("__")[1]).split("_",1)[1]
            MaskedData = masking.apply_mask((resample_to_img((results.get_map('stat')), I1)), mask)
            Arrrrr.append(np.array([(scipy.stats.pearsonr(MaskedData, MaskedData1[0]))[0],(scipy.stats.pearsonr(MaskedData, MaskedData1[1]))[0],(scipy.stats.pearsonr(MaskedData, MaskedData1[2]))[0]]))
            gc.collect()
            q=q+1
            print("Completed comparison number ", q, "out of ", len(terms), ". Name: ", term_name)
    
        Arrrrr = np.asarray(Arrrrr)
        np.save((outdir + nameconv + '%d' % (i)), Arrrrr)
        gc.collect()













def CreateListOfTermsinCSV(datasetpath, savedir, nameco):   
    import csv 
    import nimare
    import numpy as np
    ns_dset = nimare.dataset.Dataset.load(datasetpath)
    global termlist
    termlist = []
    terms = ns_dset.get_labels()
    for term in terms:
        term_name = (term.split("__")[1]).split("_",1)[1]
        termlist.append(term_name)
        term_name = []
    np.savetxt((savedir + nameco + ".csv"), termlist, delimiter =",",fmt ='% s')
def CreateListOfCoordsinCSV(datasetpath, savedir, nameconv, chunksize, namecorn):
    import nimare
    import numpy as np
    ns_dset = nimare.dataset.Dataset.load(datasetpath)
    terms = ns_dset.get_labels()
    Totl = []
    TotList = []
    dsetleng = int(len(terms)/chunksize)
    flen = (dsetleng-1)
    for i in range(flen):
        List2d = []
        CurrentA = np.load(savedir + nameconv + '%d' % (i) + ".npy")
        Currarr2d = np.reshape(CurrentA, (CurrentA.shape)[:1] + (-1,) + (CurrentA.shape)[1+2:])
        #np.concatenate(TotA, Currarr2d)
        List2d = Currarr2d.tolist()
        TotList.append(List2d)
    oddone = np.load(savedir + nameconv + '%d' % (flen) + ".npy")
    oddarr = np.reshape(oddone, (oddone.shape)[:1] + (-1,) + (oddone.shape)[1+2:])
    Totarray = np.array(TotList)
    TotColl = np.reshape(Totarray, (Totarray.shape)[:0] + (-1,) + (Totarray.shape)[0+2:]) 
    Totarrrr = np.append(TotColl,oddarr, axis=0)
    np.savetxt(savedir + namecorn + ".csv", Totarrrr, delimiter=",")

def cluster(savedir, n, weightings=False, keypath=[]):
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score
    import matplotlib.pyplot as plt
    from kneed import KneeLocator
    global ClusterCenters
    global indexedarray
    global y_clusters
    global model
    global features
    global scaled_features
    import numpy as np
    import click
    import pandas as pd
    import plotly
    termarray = np.array(termlist)
    import plotly.express as px
    if weightings == True:
        dff = pd.read_csv(keypath, delimiter = " ", header=None)
        array_values = dff.values
        strlist = array_values[:,0]
        glist = []
        for g in strlist:
            glist.append(g.split()[1])
        glist = np.array(glist).astype(float)
        #Weights = np.loadtxt(keypath,dtype='str')
        #TermWeights = Weights[:,1].astype(float)
        TermWeights = glist
        datafile = (Savedir + "DataNSCI.csv")
        labels_file = (Savedir + "NSCITerms.csv")

        data = np.genfromtxt(
            datafile,
            delimiter=",",
        )

        true_label_names = np.genfromtxt(
            labels_file,
            delimiter=",",
            dtype="str"
        )
        features = data
        true_labels = true_label_names
        scaler = StandardScaler()
        x = scaler.fit_transform(features)
        scaled_features = x
        kmeans = KMeans(
            init="random",
            n_clusters=n,
            n_init=10,
            max_iter=300,
            random_state=42
        )
        kmeans.fit(scaled_features, sample_weight=TermWeights)
        labl = kmeans.labels_
        labd = np.expand_dims(labl, axis=1)
        indexedarray = np.append(x, labd, axis=1)
        kmeans_kwargs = {
            "init": "random",
            "n_init": 10,
            "max_iter": 300,
            "random_state": 42,
        }

        # A list holds the SSE values for each k
        sse = []
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(scaled_features, sample_weight=TermWeights)
            sse.append(kmeans.inertia_)

        plt.style.use("fivethirtyeight")
        plt.plot(range(1, 11), sse)
        plt.xticks(range(1, 11))
        plt.xlabel("Number of Clusters")
        plt.ylabel("SSE")
        plt.show()

        kl = KneeLocator(
            range(1, 11), sse, curve="convex", direction="decreasing"
        )

        # A list holds the silhouette coefficients for each k
        silhouette_coefficients = []

        # Notice you start at 2 clusters for silhouette coefficient
        for k in range(2, 11):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(scaled_features, sample_weight=TermWeights)
            score = silhouette_score(scaled_features, kmeans.labels_)
            silhouette_coefficients.append(score)

        plt.style.use("fivethirtyeight")
        plt.plot(range(2, 11), silhouette_coefficients)
        plt.xticks(range(2, 11))
        plt.xlabel("Number of Clusters")
        plt.ylabel("Silhouette Coefficient")
        plt.show()

        print("Optimal number of clusters is:",kl.elbow)

        if click.confirm('Rerun analysis with optimal number of clusters?', default=True):
            kmeans = KMeans(
                init="random",
                n_clusters=kl.elbow,
                n_init=10,
                max_iter=3000,
                random_state=41
            )
            kmeans.fit(scaled_features, sample_weight=TermWeights)
            labl = kmeans.labels_
            labd = np.expand_dims(labl, axis=1)
            indexedarray = np.append(x, labd, axis=1)
            Clust1 = []
            Clust2 = []
            Clust3 = []
            Clust4 = []
            Clust5 = []
            Clust6 = []

            for x in indexedarray:
                if x[3] == 0:
                    Clust1.append(x)
                elif x[3] == 1:
                    Clust2.append(x)
                elif x[3] == 2:
                    Clust3.append(x)
                elif x[3] == 3:
                    Clust4.append(x)
                elif x[3] == 4:
                    Clust5.append(x)
                elif x[3] == 5:
                    Clust6.append(x)

            x = scaled_features
            model = KMeans(n_clusters = kl.elbow, init = "random", max_iter = 300, n_init = 10, random_state = 42)
            y_clusters = model.fit_predict(x, sample_weight=TermWeights)
            ClusterCenters = model.cluster_centers_.astype(float)
            print("Cluster centers saved as array named ClusterCenters")
            cols = ["Component 1 CorrCoef", "Component 2 CorrCoef","Component 3 CorrCoef"]
            df = pd.DataFrame(data=x, index=None, columns=cols, dtype=None, copy=None)
            df['Cluster'] = (y_clusters.reshape(-1,1) + 1).astype(str)
            df['Termnames'] = termarray
            fig = px.scatter_3d(df, x='Component 1 CorrCoef', y='Component 2 CorrCoef', z='Component 3 CorrCoef', color='Cluster', hover_name='Termnames')
            fig.show()
            fig.write_html((savedir + "plot.html"))
        else:
            kmeans = KMeans(
                init="random",
                n_clusters=n,
                n_init=10,
                max_iter=300,
                random_state=42
            )
            kmeans.fit(scaled_features, sample_weight=TermWeights)
            labl = kmeans.labels_
            labd = np.expand_dims(labl, axis=1)
            indexedarray = np.append(x, labd, axis=1)
            Clust1 = []
            Clust2 = []
            Clust3 = []
            Clust4 = []
            Clust5 = []
            Clust6 = []

            for x in indexedarray:
                if x[3] == 0:
                    Clust1.append(x)
                elif x[3] == 1:
                    Clust2.append(x)
                elif x[3] == 2:
                    Clust3.append(x)
                elif x[3] == 3:
                    Clust4.append(x)
                elif x[3] == 4:
                    Clust5.append(x)
                elif x[3] == 5:
                    Clust6.append(x)

            x = scaled_features
            model = KMeans(n_clusters = n, init = "k-means++", max_iter = 300, n_init = 10, random_state = 0)
            y_clusters = model.fit_predict(x, sample_weight=TermWeights)
            ClusterCenters = model.cluster_centers_.astype(float)
            print("Cluster centers saved as array named ClusterCenters")
            cols = ["Component 1 CorrCoef", "Component 2 CorrCoef","Component 3 CorrCoef"]
            df = pd.DataFrame(data=x, index=None, columns=cols, dtype=None, copy=None)
            df['Cluster'] = (y_clusters.reshape(-1,1) + 1).astype(str)
            df['Termnames'] = termarray
            fig = px.scatter_3d(df, x='Component 1 CorrCoef', y='Component 2 CorrCoef', z='Component 3 CorrCoef', color='Cluster', hover_name='Termnames')
            fig.show()
    else:
        datafile = (Savedir + "DataNSCI.csv")
        labels_file = (Savedir + "NSCITerms.csv")

        data = np.genfromtxt(
            datafile,
            delimiter=",",
        )

        true_label_names = np.genfromtxt(
            labels_file,
            delimiter=",",
            dtype="str"
        )
        features = data
        true_labels = true_label_names
        scaler = StandardScaler()
        x = scaler.fit_transform(features)
        scaled_features = x
        kmeans = KMeans(
            init="random",
            n_clusters=n,
            n_init=10,
            max_iter=300,
            random_state=42
        )
        kmeans.fit(scaled_features)
        labl = kmeans.labels_
        labd = np.expand_dims(labl, axis=1)
        indexedarray = np.append(x, labd, axis=1)
        kmeans_kwargs = {
            "init": "random",
            "n_init": 10,
            "max_iter": 300,
            "random_state": 42,
        }

        # A list holds the SSE values for each k
        sse = []
        for k in range(1, 11):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(scaled_features)
            sse.append(kmeans.inertia_)

        plt.style.use("fivethirtyeight")
        plt.plot(range(1, 11), sse)
        plt.xticks(range(1, 11))
        plt.xlabel("Number of Clusters")
        plt.ylabel("SSE")
        plt.show()

        kl = KneeLocator(
            range(1, 11), sse, curve="convex", direction="decreasing"
        )

        # A list holds the silhouette coefficients for each k
        silhouette_coefficients = []

        # Notice you start at 2 clusters for silhouette coefficient
        for k in range(2, 11):
            kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
            kmeans.fit(scaled_features)
            score = silhouette_score(scaled_features, kmeans.labels_)
            silhouette_coefficients.append(score)

        plt.style.use("fivethirtyeight")
        plt.plot(range(2, 11), silhouette_coefficients)
        plt.xticks(range(2, 11))
        plt.xlabel("Number of Clusters")
        plt.ylabel("Silhouette Coefficient")
        plt.show()

        print("Optimal number of clusters is:",kl.elbow)

        if click.confirm('Rerun analysis with optimal number of clusters?', default=True):
            kmeans = KMeans(
                init="random",
                n_clusters=kl.elbow,
                n_init=10,
                max_iter=3000,
                random_state=41
            )
            kmeans.fit(scaled_features)
            labl = kmeans.labels_
            labd = np.expand_dims(labl, axis=1)
            indexedarray = np.append(x, labd, axis=1)
            Clust1 = []
            Clust2 = []
            Clust3 = []
            Clust4 = []
            Clust5 = []
            Clust6 = []

            for x in indexedarray:
                if x[3] == 0:
                    Clust1.append(x)
                elif x[3] == 1:
                    Clust2.append(x)
                elif x[3] == 2:
                    Clust3.append(x)
                elif x[3] == 3:
                    Clust4.append(x)
                elif x[3] == 4:
                    Clust5.append(x)
                elif x[3] == 5:
                    Clust6.append(x)

            x = scaled_features
            model = KMeans(n_clusters = kl.elbow, init = "random", max_iter = 300, n_init = 10, random_state = 42)
            y_clusters = model.fit_predict(x)
            cols = ["Component 1 CorrCoef", "Component 2 CorrCoef","Component 3 CorrCoef"]
            df = pd.DataFrame(data=x, index=None, columns=cols, dtype=None, copy=None)
            df['Cluster'] = (y_clusters.reshape(-1,1) + 1).astype(str)
            df['Termnames'] = termarray
            fig = px.scatter_3d(df, x='Component 1 CorrCoef', y='Component 2 CorrCoef', z='Component 3 CorrCoef', color='Cluster', hover_name='Termnames')
            fig.show()
            ClusterCenters = model.cluster_centers_.astype(float)
            print("Cluster centers saved as array named ClusterCenters")

        else:
            kmeans = KMeans(
                init="random",
                n_clusters=n,
                n_init=10,
                max_iter=300,
                random_state=42
            )
            kmeans.fit(scaled_features)
            labl = kmeans.labels_
            labd = np.expand_dims(labl, axis=1)
            indexedarray = np.append(x, labd, axis=1)
            Clust1 = []
            Clust2 = []
            Clust3 = []
            Clust4 = []
            Clust5 = []
            Clust6 = []

            for x in indexedarray:
                if x[3] == 0:
                    Clust1.append(x)
                elif x[3] == 1:
                    Clust2.append(x)
                elif x[3] == 2:
                    Clust3.append(x)
                elif x[3] == 3:
                    Clust4.append(x)
                elif x[3] == 4:
                    Clust5.append(x)
                elif x[3] == 5:
                    Clust6.append(x)

            x = scaled_features
            model = KMeans(n_clusters = n, init = "k-means++", max_iter = 300, n_init = 10, random_state = 0)
            y_clusters = model.fit_predict(x)
            cols = ["Component 1 CorrCoef", "Component 2 CorrCoef","Component 3 CorrCoef"]
            df = pd.DataFrame(data=x, index=None, columns=cols, dtype=None, copy=None)
            df['Cluster'] = (y_clusters.reshape(-1,1) + 1).astype(str)
            df['Termnames'] = termarray
            fig = px.scatter_3d(df, x='Component 1 CorrCoef', y='Component 2 CorrCoef', z='Component 3 CorrCoef', color='Cluster', hover_name='Termnames')
            fig.show()
            ClusterCenters = model.cluster_centers_.astype(float)
            print("Cluster centers saved as array named ClusterCenters")
            
def standardizeandsort():
    import sklearn
    import numpy as np
    global StandardizedDists
    def distance_finder(one,two) :
        [x1,y1,z1] = one  # first coordinates
        [x2,y2,z2] = two  # second coordinates
        return (((x2-x1)**2)+((y2-y1)**2)+((z2-z1)**2))**(1/2)
    termarray = np.asarray(termlist)
    termarray = np.expand_dims(termarray, axis=1)
    toermar = np.append(termarray, indexedarray, axis=1)
    CDistances = []
    CDists = []
    C2Distances = []
    C3Distances = []
    C4Distances = []
    CDistlists = []
    scaler = sklearn.preprocessing.StandardScaler()
    l = len(ClusterCenters)
    #CDistances = np.expand_dims(CDistance, axis=1)
    for q in toermar:
        q1 = q[1:4].astype(float)
        CDist = []
        CDistances = []
        for cnum in ClusterCenters:
            ctemp = []
            ctemp = distance_finder(q1,cnum)
            CDistances.append(ctemp)
           # CR = np.transpose(np.array(CDistances))
         #   CR = np.array(ctemp).reshape(-1, 1)
         #   CDapp = np.append(np.expand_dims(CDist,0), CR , axis=1)
       # CR = np.transpose(np.array(CDistances)).tolist()
        CR = (np.transpose(np.array(CDistances).reshape(-1, 1)))
        CRs = np.reshape(CR, (CR.shape)[:0] + (-1,) + (CR.shape)[0+2:])
        CDists.append(CRs)
        CDArr = np.array(CDists)
    for y in range(CDArr.shape[1]):
        Cvs = []
        scaler.fit(np.transpose(CDArr)[y].reshape(-1, 1))
        Cvs = (-scaler.transform(np.transpose(CDArr)[y].reshape(-1, 1))).tolist()
        CDistlists.append(Cvs)
    StandardizedDists = np.array(CDistlists).astype(float).reshape(len(toermar), l)
    return "Complete"



def saveloadings(Savedir,  Upper_Vals = 10, Lower_Vals = 10):
    global terdir
    global loadir
    import numpy as np
    termarray = np.asarray(termlist)
    termarray = np.expand_dims(termarray, axis=1)
    toermar = np.append(termarray, indexedarray, axis=1)
    CSq = np.squeeze(StandardizedDists)
    C1WithTerm = np.append(CSq, termarray, axis=1)
    claor = C1WithTerm.tolist()
    CDistsrs = np.append(CSq, termarray, axis=1)
    x = C1WithTerm
    for i in range(StandardizedDists.shape[1]):
        ByC = sorted(C1WithTerm, key=lambda x:x[i].astype(float),reverse=True)
        ByCa = np.array(ByC)
        Top10 = np.append(ByCa[0:Upper_Vals],ByCa[(len(ByC)-Lower_Vals):(len(ByC))],axis=0) 
        Tsor = np.append(np.expand_dims(Top10[:,i].astype(float), axis=1),np.expand_dims(Top10[:,StandardizedDists.shape[1]],axis=1), axis=1)
        Loadings = Tsor[:,0].astype(float)
        termls = Tsor[:,1]
        terdir = (Savedir + "ClusterTerms" + '%d' %(i+1) + ".csv")
        loadir = (Savedir + "ClusterLoadings" + '%d' %(i+1) + ".csv")
        np.savetxt(Savedir + "ClusterTerms" + '%d' %(i+1) + ".csv", termls, delimiter =",",fmt ='% s') 
        np.savetxt(Savedir + "ClusterLoadings" + '%d' %(i+1) + ".csv", Loadings, delimiter =",",fmt ='% s') 
        


# %% Read in data
# read in neurosynth term loading data for caps 5 & 6
def Cloud(Savedir, outdir):
    import pandas as pd
    from collections import OrderedDict
    from wordcloud import WordCloud
    import matplotlib.cm as cm
    import matplotlib.colors as mcolor
    import os
    import numpy as np
    folder_path = Savedir

    p=[]
    for p in range(StandardizedDists.shape[1]):
        data_path = (Savedir + "ClusterLoadings" + '%d' %(p+1) + ".csv")
        df = pd.read_csv(data_path, header=None)


        # read in display labels
        label_path = (Savedir + "ClusterTerms" + '%d' %(p+1) + ".csv")
        display = pd.read_csv(label_path, header=None)


    # transform to dictionary for word cloud function 
        neurosynth_dict = OrderedDict()
        neurosynth_dict['neurosynth'] = df
    
    # change directory for saving results
        os.chdir(outdir)

    # call word cloud function 
        #wordclouder(neurosynth_dict, display, savefile=False)
    
        for key, value in neurosynth_dict.items(): # Loop over loading dictionaries - 1 dataframe per iteration
            df = pd.DataFrame(value) 
            principle_vector = np.array(df, dtype =float) # turn df into array
            pv_in_hex= []
            vmax = np.abs(principle_vector).max() #get the maximum absolute value in array
            vmin = -vmax #minimu 
            for i in range(principle_vector.shape[1]): # loop through each column (cap)
                rescale = (principle_vector  [:,i] - vmin) / (vmax - vmin) # rescale scores 
                colors_hex = []
                for c in cm.RdBu_r(rescale): 
                    colors_hex.append(mcolor.to_hex(c)) # adds colour codes (hex) to list
                pv_in_hex.append(colors_hex) # add all colour codes for each item on all caps 
            colors_hex = np.array(pv_in_hex ).T 
            df_v_color = pd.DataFrame(colors_hex)

        # loops over loadings for each cap
            for col_index in df:
                absolute = df[col_index].abs() # make absolute 
                integer = 100 * absolute # make interger 
                integer = integer.astype(int) 
                concat = pd.concat([integer, df_v_color[col_index]], axis=1) # concatanate loadings and colours 
                concat.columns = ['freq', 'colours']
                concat.insert(1, 'labels', display[col_index]) # add labels (items) from display df
          
                freq_dict = dict(zip(concat.labels, concat.freq)) # where key: item and value: weighting
                colour_dict = dict(zip(concat.labels, concat.colours))# where key: itemm and value: colour
                def color_func(word, *args, **kwargs): #colour function to supply to wordcloud function.. don't ask !
                    try:
                        color = colour_dict[word]
                    except KeyError:
                        color = '#000000' # black
                    return color
                # create wordcloud object
                wc = WordCloud(background_color="white", color_func=color_func, 
                            width=400, height=400, prefer_horizontal=1, 
                            min_font_size=8, max_font_size=200
                            )
            # generate wordcloud from loadings in frequency dict

        wc = wc.generate_from_frequencies((freq_dict))
        wc.to_file('WordCloudCluster%d.png'.format(key, col_index+5) %(p+1)) 





#%%
Constructandsave(database, annotationsnew2, outdir2)

#CompareCorr(datasetpath, Savedir, name, .1, 2)

#CreateListOfTermsinCSV(datasetpath, Savedir, "NSCITerms")

#CreateListOfCoordsinCSV(datasetpath, Savedir, name, 2, "DataNSCI")

#cluster(Savedir, 6, weightings=True, keypath=keypath)

#standardizeandsort()

#saveloadings(Savedir, Lower_Vals = 0)

#Cloud(Savedir, Savedir)
# %%

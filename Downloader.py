import os
import nimare
import requests
import tarfile
import gc
from numba import jit, cuda
@jit(target ="cuda")
def DownloadandConstruct():
    if (os.path.exists('tempDir') == False):
        os.mkdir('tempDir')
    if (os.path.exists('Data') == False):
        os.mkdir('Data')
    if (os.path.exists('Gradients') == False):
        os.mkdir('Gradients')
    if (os.path.exists('Topics') == False):
        os.mkdir('Topics')
    if (os.path.exists('Features') == False):
        os.mkdir('Features')

    url1 = "https://github.com/neurosynth/neurosynth-data/blob/master/current_data.tar.gz?raw=true"
    resp1 = requests.get(url1, stream=True)
    print(resp1.headers.get('content-type'))
    with open('tempDir/current_data', 'wb') as fd1:
        for chunk1 in resp1.iter_content(chunk_size=128):
            fd1.write(chunk1)
    tarfile.open('tempDir/current_data').extractall(path='Data')
    #dbase = 'tempDir/database.txt'
    #feats = 'tempDir/features.txt'
    print("datafile is opened, creating...")

    gc.collect()
    os.remove('tempDir/current_data')

    print("creating gradients")
    url2 = "https://github.com/17iwgh/dbasepub/blob/main/GradRepo.tar?raw=true"
    resp2 = requests.get(url2, stream=True)
    with open('tempDir/Gradients', 'wb') as fd2:
        for chunk2 in resp2.iter_content(chunk_size=128):
            fd2.write(chunk2)
    tarfile.open('tempDir/Gradients').extractall(path='Gradients')
    gc.collect()
    os.remove('tempDir/Gradients')

    print("creating topics")
    url3 = "https://github.com/neurosynth/neurosynth-data/blob/master/topics/v5-topics.tar.gz?raw=true"
    resp3 = requests.get(url3, stream=True)
    with open('tempDir/Topics', 'wb') as fd3:
        for chunk3 in resp3.iter_content(chunk_size=128):
            fd3.write(chunk3)
    tarfile.open('tempDir/Topics').extractall(path='Topics')
    gc.collect()
    os.remove('tempDir/Topics')


    print("preparing features")

    for idx, i in enumerate(os.listdir('Topics/analyses')):
        src=open(("Topics/analyses/" + i),"r") 
        fline="pm"    #Prepending string 
        oline=src.readlines() 
        #Here, we prepend the string we want to on first line 
        oline.insert(0,fline) 
        src.close() 
        #We again open the file in WRITE mode  
        src=open(("Topics/analyses/" + i),"w") 
        src.writelines(oline) 
        src.close()
        os.replace(("Topics/analyses/" + i), ("Features/" + i)) 
        #We read the existing text from file in READ mode 

    os.replace("Data/features.txt", "Features/v5-fulldataset.txt")

    print("creating datasets")

    if (os.path.exists('Packaged_Datasets') == False):
        os.mkdir('Packaged_Datasets')

    for idx, i in enumerate(os.listdir('Features')):
        ns_dset = nimare.io.convert_neurosynth_to_dataset("Data/database.txt",annotations_file=("Features/" + i))
        ns_dset.save("Packaged_Datasets/%s.pkl" % (i.split(".")[0])) 

DownloadandConstruct()
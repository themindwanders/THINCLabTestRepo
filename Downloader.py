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
print("datafile is opened, creating...")
ns_dset = nimare.io.convert_neurosynth_to_dataset(dbase,annotations_file=feats)
ns_dset.save('Data/currentDatabase.pkl')
print("dataset created")
gc.collect()
os.remove('tempDir/database.txt')
os.remove('tempDir/features.txt')
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
import os
from typing import Dict
import pandas as pd
import sklearn
import numpy as np
from sklearn import preprocessing
import pandas as pd
from collections import OrderedDict
from wordcloud import WordCloud
import matplotlib.cm as cm
import matplotlib.colors as mcolor
import os
import numpy as np
def distance_finder(one,two) :
    [x1,y1,z1] = one  # first coordinates
    [x2,y2,z2] = two  # second coordinates
    return (((x2-x1)**2)+((y2-y1)**2)+((z2-z1)**2))**(1/2)
demo = [0.04 , 0.1, 0.05]

for idx, i in enumerate(os.listdir('CSVData')):
    path = os.path.join('CSVData', i)
    Dframe = pd.read_csv(path, header=None, names=['Term','Coordinates'])
    Dframe.set_index('Term')
    print(Dframe)
    dfdists = pd.DataFrame(columns=['Term', 'Distance'])
    for ind, i in Dframe.iterrows():
        rowval = i['Coordinates'].strip('][').split(', ')
        for id, d in enumerate(rowval):
            rowval[id] = float(rowval[id])
        distance = distance_finder(demo,rowval)
        listst = [i['Term'], distance]
        dfdists.loc[ind] = listst

        print(listst)
    #dfdists.set_index('Term')
    dfsorted = dfdists.sort_values(by ='Distance', axis=0, ascending=False)
    scaler = sklearn.preprocessing.StandardScaler()
    dfsorted['Distance'] = scaler.fit_transform(np.asarray(dfsorted['Distance']).reshape(-1, 1))
    top10 = dfsorted[:10]

if (os.path.exists('Clouds') == False):
    os.mkdir('Clouds')

Dictver = np.array(top10['Distance'])
Dispver = np.array(top10['Term'])
Dictver = dict(enumerate(Dictver.flatten(), 1))
print(Dictver)
import os
import pandas as pd
import numpy as np
from collections import OrderedDict

from wordcloud import WordCloud
import matplotlib.cm as cm
import matplotlib.colors as mcolor




wc = WordCloud(background_color="white", color_func=color_func, 
                width=400, height=400, prefer_horizontal=1, 
                min_font_size=8, max_font_size=200
                )
            # generate wordcloud from loadings in frequency dict
wc = wc.generate_from_frequencies(freq_dict)
wc.to_file('{}_wordcloud_cap_{}.png'.format(key, col_index+5))








# df = top10['Distance']
#     # read in display labels
# display = top10['Term']


#     # transform to dictionary for word cloud function 
# neurosynth_dict = OrderedDict()
# neurosynth_dict['neurosynth'] = df
    
#     # change directory for saving results
# os.chdir('Clouds')

#     # call word cloud function 
# #wordclouder(neurosynth_dict, display, savefile=False)
    
# for key, value in neurosynth_dict.items(): # Loop over loading dictionaries - 1 dataframe per iteration
#     df = pd.DataFrame(value) 
#     principle_vector = np.array(df, dtype =float) # turn df into array
#     pv_in_hex= []
#     vmax = np.abs(principle_vector).max() #get the maximum absolute value in array
#     vmin = -vmax #minimu 
#     for i in range(principle_vector.shape[1]): # loop through each column (cap)
#         rescale = (principle_vector  [:,i] - vmin) / (vmax - vmin) # rescale scores 
#         colors_hex = []
#         for c in cm.RdBu_r(rescale): 
#             colors_hex.append(mcolor.to_hex(c)) # adds colour codes (hex) to list
#         pv_in_hex.append(colors_hex) # add all colour codes for each item on all caps 
#     colors_hex = np.array(pv_in_hex ).T 
#     df_v_color = pd.DataFrame(colors_hex)

#         # loops over loadings for each cap
#     for inter, col_index in enumerate(df):
#         absolute = df[col_index].abs() # make absolute 
#         integer = 100 * absolute # make interger 
#         integer = integer.astype(int) 
#         print(inter)
#         concat = pd.concat([integer, df_v_color[inter]], axis=1) # concatanate loadings and colours 
#         concat.columns = ['freq', 'colours']
#         concat.insert(1, 'labels', display) # add labels (items) from display df
#         freq_dict = dict(zip(concat.labels, concat.freq)) # where key: item and value: weighting
#         colour_dict = dict(zip(concat.labels, concat.colours))# where key: itemm and value: colour
#         def color_func(word, *args, **kwargs): #colour function to supply to wordcloud function.. don't ask !
#             try:
#                 color = colour_dict[word]
#             except KeyError:
#                 color = '#000000' # black
#             return color
#                 # create wordcloud object
#         wc = WordCloud(background_color="white", color_func=color_func, 
#                     width=400, height=400, prefer_horizontal=1, 
#                     min_font_size=8, max_font_size=200
#                     )
#             # generate wordcloud from loadings in frequency dict

# wc = wc.generate_from_frequencies((freq_dict))
# wc.to_file('WordCloudCluster.png') 






# def standardizeandsort():
#     import sklearn
#     import numpy as np
#     import pandas as pd
    
#     def distance_finder(one,two) :
#         [x1,y1,z1] = one  # first coordinates
#         [x2,y2,z2] = two  # second coordinates
#         return (((x2-x1)**2)+((y2-y1)**2)+((z2-z1)**2))**(1/2)

#     termarray = np.asarray(termlist)
#     termarray = np.expand_dims(termarray, axis=1)
#     toermar = np.append(termarray, indexedarray, axis=1)
#     CDistances = []
#     CDists = []
#     CDistlists = []
#     scaler = sklearn.preprocessing.StandardScaler()
#     l = len(ClusterCenters)
#     #CDistances = np.expand_dims(CDistance, axis=1)
#     for q in toermar:
#         q1 = q[1:4].astype(float)
#         CDist = []
#         CDistances = []
#         for cnum in ClusterCenters:
#             ctemp = []
#             ctemp = distance_finder(q1,cnum)
#             CDistances.append(ctemp)
#            # CR = np.transpose(np.array(CDistances))
#          #   CR = np.array(ctemp).reshape(-1, 1)
#          #   CDapp = np.append(np.expand_dims(CDist,0), CR , axis=1)
#        # CR = np.transpose(np.array(CDistances)).tolist()
#         CR = (np.transpose(np.array(CDistances).reshape(-1, 1)))
#         CRs = np.reshape(CR, (CR.shape)[:0] + (-1,) + (CR.shape)[0+2:])
#         CDists.append(CRs)
#         CDArr = np.array(CDists)
#     for y in range(CDArr.shape[1]):
#         Cvs = []
#         scaler.fit(np.transpose(CDArr)[y].reshape(-1, 1))
#         Cvs = (-scaler.transform(np.transpose(CDArr)[y].reshape(-1, 1))).tolist()
#         CDistlists.append(Cvs)
#     StandardizedDists = np.array(CDistlists).astype(float).reshape(len(toermar), l)
#     return "Complete"



# def saveloadings(Savedir,  Upper_Vals = 10, Lower_Vals = 10):
#     global terdir
#     global loadir
#     import numpy as np
#     termarray = np.asarray(termlist)
#     termarray = np.expand_dims(termarray, axis=1)
#     toermar = np.append(termarray, indexedarray, axis=1)
#     CSq = np.squeeze(StandardizedDists)
#     C1WithTerm = np.append(CSq, termarray, axis=1)
#     claor = C1WithTerm.tolist()
#     CDistsrs = np.append(CSq, termarray, axis=1)
#     x = C1WithTerm
#     for i in range(StandardizedDists.shape[1]):
#         ByC = sorted(C1WithTerm, key=lambda x:x[i].astype(float),reverse=True)
#         ByCa = np.array(ByC)
#         Top10 = np.append(ByCa[0:Upper_Vals],ByCa[(len(ByC)-Lower_Vals):(len(ByC))],axis=0) 
#         Tsor = np.append(np.expand_dims(Top10[:,i].astype(float), axis=1),np.expand_dims(Top10[:,StandardizedDists.shape[1]],axis=1), axis=1)
#         Loadings = Tsor[:,0].astype(float)
#         termls = Tsor[:,1]
#         terdir = (Savedir + "ClusterTerms" + '%d' %(i+1) + ".csv")
#         loadir = (Savedir + "ClusterLoadings" + '%d' %(i+1) + ".csv")
#         np.savetxt(Savedir + "ClusterTerms" + '%d' %(i+1) + ".csv", termls, delimiter =",",fmt ='% s') 
#         np.savetxt(Savedir + "ClusterLoadings" + '%d' %(i+1) + ".csv", Loadings, delimiter =",",fmt ='% s') 
        


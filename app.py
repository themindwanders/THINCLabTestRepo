import base64
import os
import nimare
import requests
import tarfile
import gc
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

status = "nothing"
UPLOAD_DIRECTORY = 'Downloads'

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(server=server)


@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


app.layout = html.Div(
    [
        html.Button('Download and Construct Datasets', id='btn-nclicks-1', n_clicks=0),
        html.H1("File Browser"),
        html.H2("Upload"),
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["Drag and drop or click to select a file to upload."]
            ),
            style={
                "width": "100%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.Button('Button 2', id='btn-nclicks-2', n_clicks=0),
        html.H2("File List"),
        html.Ul(id="file-list"),
        html.Div(id='update-text')
    ],
    style={"max-width": "500px"},
)


@app.callback(Output('update-text', 'children'),
              Input('btn-nclicks-1', 'n_clicks'),
              Input('btn-nclicks-2', 'n_clicks')       
)
def displayClick(btn1, btn2):
    global clickbtn1
    global clickbtn2
    global status
    status = "nothing"
    html.Div(status)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'btn-nclicks-1' in changed_id:
        clickbtn1 = True
        status = "starting"
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
        status = resp1.headers.get('content-type')
        html.Li(status)
        with open('tempDir/current_data', 'wb') as fd1:
            for chunk1 in resp1.iter_content(chunk_size=128):
                fd1.write(chunk1)
        tarfile.open('tempDir/current_data').extractall(path='Data')
        #dbase = 'tempDir/database.txt'
        #feats = 'tempDir/features.txt'
        status = "datafile is opened, creating..."
        html.Li(status)
        gc.collect()
        os.remove('tempDir/current_data')

        status = "creating gradients"
        url2 = "https://github.com/17iwgh/dbasepub/blob/main/GradRepo.tar?raw=true"
        resp2 = requests.get(url2, stream=True)
        with open('tempDir/Gradients', 'wb') as fd2:
            for chunk2 in resp2.iter_content(chunk_size=128):
                fd2.write(chunk2)
        tarfile.open('tempDir/Gradients').extractall(path='Gradients')
        gc.collect()
        os.remove('tempDir/Gradients')

        status = "creating topics"
        url3 = "https://github.com/neurosynth/neurosynth-data/blob/master/topics/v5-topics.tar.gz?raw=true"
        resp3 = requests.get(url3, stream=True)
        with open('tempDir/Topics', 'wb') as fd3:
            for chunk3 in resp3.iter_content(chunk_size=128):
                fd3.write(chunk3)
        tarfile.open('tempDir/Topics').extractall(path='Topics')
        gc.collect()
        os.remove('tempDir/Topics')


        status = "preparing features"

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

        status = "creating datasets"

        if (os.path.exists('Packaged_Datasets') == False):
            os.mkdir('Packaged_Datasets')

        for idx, i in enumerate(os.listdir('Features')):
            ns_dset = nimare.io.convert_neurosynth_to_dataset("Data/database.txt",annotations_file=("Features/" + i))
            ns_dset.save("Packaged_Datasets/%s.pkl" % (i.split(".")[0])) 
    elif 'btn-nclicks-2' in changed_id:
        clickbtn2 = True




def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


@app.callback(
    Output("file-list", "children"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],

)



def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""
    #Processing = False
    #if not n_clicks == 0:
    #    n_clicks = 0
    #    print("Click")
    #    Processing = True
    #if Processing == True:
    #    if uploaded_files() == []:
    #        return html.Div("nothing to work with")
    #    else:
    #        html.Div("working...")
    #        return html.Div(uploaded_files())

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [html.Li(file_download_link(filename)) for filename in files]




if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
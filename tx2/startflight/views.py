from django.shortcuts import render
from django.http import  HttpResponseRedirect
from django.urls import reverse
from .forms import InputForm
from configparser import ConfigParser
import os
import logging
import subprocess 

log = logging.getLogger(__name__)

def home_view(request):

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        
        # create a form instance and populate it with data from the request:
        form = InputForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            data = form.cleaned_data
            save_configs(data)
            flightname = data['flightname']
            # read configs file
            config = ConfigParser()
            config.read(os.path.join(*['/home/jetsontx2/Documents/django/tx2/Flights',  flightname,  'log','config.ini']))
            logging.basicConfig(filename=os.path.join(config.get('dirs',  'logdir'), "flight.log"),  level=logging.INFO)
            request.session['formdata'] = request.POST

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('monitor:monitoring_view', args=(flightname,)))

    # if a GET (or any other method) we'll create a blank form
    else:
        form = {}
        form['form'] = InputForm()

    return render(request, "startflight/home.html", form)


def save_configs(data):
    config = ConfigParser()

    config.read('config.ini')

    # Parse flight configurations
    deeplearningmodels = {'0': 'none', '1':'MultEYE (object)', '2':'MultEYE (segmentation)'}
    cameratypes = {'0':'PTP-device (SODA)',  '1':'usb-camera'}
    gcstypes = {'0':'Alienware',  '1':'FTP-server', '2':'Desktop'}
    networktypes = {'0':'panoptis@192.168.1.250',  '1':'sofia@192.168.1.25'}
    compressed = {'0': 'yes'}
    choices = {
                '0': 'original',
                '1': 'images',
                '2': 'labels'
                }

    #data = request.session.get('formdata')
    flightname = data['flightname']
    model = deeplearningmodels[data['model']]
    camera = cameratypes[data['camera']]
    gcs = gcstypes[data['groundstation']]
    network = networktypes[data['groundstation']]
    transfer = [i for i in data['transfers']]
    print(data['compressed'])
    if data['compressed']:
        compr = compressed[data['compressed'][0]]
    else: 
        compr = 'no'
    notes = data['notes']
    
    #config.add_section('main') TODO: make condition to check whether section already exists
    config.set('main', 'flightname', flightname)
    config.set('main', 'model', model)
    config.set('main', 'camera',  camera)
    config.set('main',  'gcs',  gcs)
    for i in range(len(choices)):
        if str(i) in transfer:
            config.set('main', 't'+str(i), 'True')
        else:
            config.set('main', 't'+str(i), 'False')
    config.set('main',  'compressed',  compr)
    config.set('main', 'notes', notes)
    
    config.set('network',  'address',  network)
    
    # Create and store dirs
    #config.add_section('dirs') # TODO: make condition to check whether section already exists
    
    dirs = []
    maindir = '/home/jetsontx2/Documents/django/tx2/Flights/{}'.format(flightname)
    sodadir = os.path.join(maindir, 'SODA_images')
    logdir = os.path.join(maindir, 'log')
    sodadir_thumb = os.path.join(maindir, 'SODA_images_thumb') 
    
    dirs.append(maindir)
    dirs.append(sodadir)
    dirs.append(sodadir_thumb)
    dirs.append(logdir)
    
    config.set('dirs', 'maindir', maindir)
    config.set('dirs', 'sodadir', sodadir)
    config.set('dirs', 'sodadir_thumb', sodadir_thumb)
    config.set('dirs', 'logdir', logdir)
    
    if gcs == 'FTP-server':
        rmtdirs = []
        rmtdir = os.path.join("/pub/DeltaQuad",  flightname)
        rmt_sodadir = os.path.join(rmtdir,  "SODA_images")
        rmt_logdir = os.path.join(rmtdir,  "log")
        
        rmtdirs.append(rmt_sodadir)
        rmtdirs.append(rmt_logdir)
        
        config.set('rmt', 'sodadir', rmt_sodadir)
        config.set('rmt', 'logdir', rmt_logdir)
        subprocess.call(["startflight/utils/create_rmt_dirs.sh",  rmtdir])
        subprocess.call(["startflight/utils/create_rmt_dirs.sh",  rmt_sodadir])
        subprocess.call(["startflight/utils/create_rmt_dirs.sh",  rmt_logdir])

    if model != 'none':
        detectiondir = os.path.join(maindir, 'detections')
        segmentationdir = os.path.join(maindir, 'segmentations')
        dirs.append(detectiondir)
        dirs.append(segmentationdir)
        
        config.set('dirs', 'detectiondir', detectiondir)
        config.set('dirs', 'segmentationdir', segmentationdir)
        
        if gcs == 'FTP-server':
            rmt_segdir= os.path.join(rmtdir, "segmentations")
            rmt_objdir= os.path.join(rmtdir, "detections")
            rmtdirs.append(rmt_segdir)
            rmtdirs.append(rmt_objdir)
            
            config.set('rmt', 'detectiondir', rmt_objdir)
            config.set('rmt', 'segmentationdir', rmt_segdir)
            
            subprocess.call(["startflight/utils/create_rmt_dirs.sh",  rmt_segdir])
            subprocess.call(["startflight/utils/create_rmt_dirs.sh",  rmt_objdir])

    for i in dirs:
        if not os.path.exists(i):
            os.makedirs(i)    
    
    with open('config.ini', 'w') as f:
        config.write(f)
    with open(os.path.join(logdir, 'config.ini'), 'w') as f:
        config.write(f)

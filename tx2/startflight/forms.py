from django import forms
from datetime import datetime

# creating a form
class InputForm(forms.Form):
    now = datetime.now()
    date_time = now.strftime("%d%m%y_%H%M")
    default_flightname = "flight_" + date_time
    flightname = forms.CharField(widget=forms.TextInput(attrs={'placeholder': default_flightname}), initial=default_flightname, required=False)
    deeplearningmodels = ['none', 'MultEYE (object)', 'MultEYE (segmentation)']
    model = forms.ChoiceField(choices=[(idx, i) for idx, i in enumerate(deeplearningmodels)], initial=0, required=False)
    cameratypes = ['PTP-device (SODA)',  'usb-camera']
    camera = forms.ChoiceField(choices=[(idx, i) for idx, i in enumerate(cameratypes)], initial=0, required=True)
    groundstationtypes = ['Alienware',  'FTP-server', 'desktop']
    groundstation = forms.ChoiceField(choices=[(idx, i) for idx, i in enumerate(groundstationtypes)], initial=1, required=True)
    transfers = forms.MultipleChoiceField(
                                   widget=forms.CheckboxSelectMultiple(),
                                   choices=[('0', 'original'),
                                            ('1', 'images'),
                                            ('2', 'labels')],
                                   required=False)
    compressed = forms.MultipleChoiceField(
                                   widget=forms.CheckboxSelectMultiple(),
                                   choices=[('0', 'yes')],  
                                            required=False)
    #notes = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ''}), initial='',  max_length=500, required=False)
    notes = forms.CharField(widget=forms.TextInput(attrs={'placeholder': ' '}), initial=' ', max_length=500,  required=False)
    
def __init__(self, *args, **kwargs):
    self.helper.layout = Layout(Row(
        Column('check_1',css_class='col-md-6',),
        Column('check_2',css_class='col-md-6',),
        Column('check_3', css_class='col-md-6',),
        Column('check_4', css_class='col-md-6',),
        css_class='form-row'))

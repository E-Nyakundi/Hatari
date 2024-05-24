from django import forms

class DownloadForm(forms.Form):
    url = forms.URLField(label='Video/Playlist URL', required=True, widget=forms.URLInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter video or playlist URL'
    }))
    QUALITY_CHOICES = [
        ('128K', '128K'),
        ('256K', '256K'),
        ('360P', '360P'),
        ('480P', '480P'),
        ('720P', '720P'),
        ('1080P', '1080P'),
    ]
    selected_quality = forms.ChoiceField(label='Select Quality', choices=QUALITY_CHOICES, required=False, widget=forms.RadioSelect)

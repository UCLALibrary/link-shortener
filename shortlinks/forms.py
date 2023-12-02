from django import forms
from shortlinks.models import Link


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["short_path", "target_url"]

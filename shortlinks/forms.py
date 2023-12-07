from django import forms
from shortlinks.models import Link


class LinkForm(forms.ModelForm):
    class Meta:
        model = Link
        fields = ["short_path", "target_url"]
        labels = {"target_url": "Target URL"}
        widgets = {
            "short_path": forms.TextInput(attrs={"placeholder": "e.g., /lib"}),
            "target_url": forms.URLInput(
                attrs={"placeholder": "e.g., https://www.library.ucla.edu"}
            ),
        }

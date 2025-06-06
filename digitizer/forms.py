from django import forms

class BarChartForm(forms.Form):
    original_image = forms.ImageField(
        label="Bar Chart Image",
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    p1_value = forms.IntegerField(
        label="Baseline",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1',
            'min': '0',
        }),
        help_text="Baseline"
    )
    p2_value = forms.IntegerField(
        label="Second point in y axis",
        widget=forms.NumberInput(
            attrs={
                'class':'form-control',
                'step': '1',
                'min':'0'
            }
        )
    )

    # Add x coordinates for both points
    x1 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    x2 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    y1 = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    y2 = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        x1 = cleaned_data.get('x1')
        y1 = cleaned_data.get('y1')
        x2 = cleaned_data.get('x2')
        y2 = cleaned_data.get('y2')
          
        if not x1 or not y1 or not x2 or not y2:
            raise forms.ValidationError("Please select two points on the chart for calibration")
        
        # Relaxed validation for vertical alignment
        if abs(x1 - x2) > 50:  # Increased threshold to 50px
            raise forms.ValidationError("Calibration points should be vertically aligned")
        
        if abs(y1 - y2) < 10:  # Points should have different y coordinates
            raise forms.ValidationError("Calibration points must be vertically separated by at least 10 pixels")
        
        return cleaned_data
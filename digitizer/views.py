from django.shortcuts import render
from django.conf import settings
from .forms import BarChartForm
from .utils import digitize_barchart
import os
import uuid
from django.core.files.storage import default_storage

def index(request):
    if request.method == 'POST':
        form = BarChartForm(request.POST, request.FILES)
        if form.is_valid():
            # Process the image
            image = form.cleaned_data['original_image']
            
            # Create a unique filename
            unique_id = uuid.uuid4().hex
            orig_filename = f"temp_{unique_id}_{image.name}"
            analyzed_filename = f"analyzed_{unique_id}_{image.name}"
            
            # Save original image temporarily
            orig_path = os.path.join(settings.MEDIA_ROOT, 'uploads', orig_filename)
            os.makedirs(os.path.dirname(orig_path), exist_ok=True)
            with open(orig_path, 'wb+') as f:
                for chunk in image.chunks():
                    f.write(chunk)
            
            # Process the image
            x1 = form.cleaned_data['x1']
            y1 = form.cleaned_data['y1']
            x2 = form.cleaned_data['x2']
            y2 = form.cleaned_data['y2']
            p1_value = form.cleaned_data['p1_value']
            p2_value = form.cleaned_data['p2_value']
            value_diff = p2_value - p1_value 
            
            try:
                bars,total1,total2, analyzed_path = digitize_barchart(
                    orig_path,
                    x1, y1, x2, y2,
                    p1_value,
                    p2_value
                )
                
                # Get URL for analyzed image
                analyzed_url = f"/media/analyzed/{os.path.basename(analyzed_path)}"
                
                # Clean up original image after processing
                os.remove(orig_path)
                
                return render(request, 'digitizer/results.html', {
                    'bars': bars,
                    'total1': total1,
                    'total2':total2,
                    'analyzed_image_url': analyzed_url
                })
                
            except Exception as e:
                # Clean up on error
                if os.path.exists(orig_path):
                    os.remove(orig_path)
                return render(request, 'digitizer/index.html', {
                    'form': form,
                    'error': f"Error processing image: {str(e)}"
                })
        else:
             # Display form errors to user
            return render(request, 'digitizer/index.html', {
                'form': form,
                'error': "Please correct the errors below"
            })
    else:
        form = BarChartForm()
    
    return render(request, 'digitizer/index.html', {'form': form})
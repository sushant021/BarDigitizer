import os
import tempfile
import cv2
import base64
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from digitizer.utils import digitize_barchart
from .serializers import BarChartDigitizerSerializer

class BarChartDigitizerAPI(APIView):
    def post(self, request):
        serializer = BarChartDigitizerSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        data = serializer.validated_data
        image = data['image']
        
        # Save image to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            for chunk in image.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            # Process image
            results = digitize_barchart(
                tmp_path,
                data['x1'], data['y1'],
                data['x2'], data['y2'],
                data['p1_value'],
                data['p2_value']
            )
            
            bars, total1, total2, output_img = results
            
            # Convert output image to base64
            _, buffer = cv2.imencode('.jpg', output_img)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            os.unlink(tmp_path)  # Clean up temp file

        return Response({
            'bars': bars,
            'total1': total1,
            'total2': total2,
            #'analyzed_image': img_base64
        })
    
      
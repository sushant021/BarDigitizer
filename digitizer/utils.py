import cv2
import numpy as np
import os
from django.conf import settings

def calculate_heights(cnt):
    """Calculate bar heights from contour points with robust error handling"""
    # Reshape contour to get list of points
    points = cnt.reshape(-1, 2)
    
    # Extract x and y coordinates
    x_coords = points[:, 0]
    y_coords = points[:, 1]
    
    # Find max y (lowest point)
    max_y = np.max(y_coords)
    
    # Find all points at or near max_y (within 1 pixel)
    base_points = points[np.abs(y_coords - max_y) <= 1]
    
    if len(base_points) == 0:
        return (0, 0)
    
    # Find leftmost and rightmost base points
    min_x = np.min(base_points[:, 0])
    max_x = np.max(base_points[:, 0])
    
    # Find BP1 (left base point)
    bp1_candidates = base_points[base_points[:, 0] == min_x]
    BP1 = bp1_candidates[0] if len(bp1_candidates) > 0 else None
    
    # Find BP2 (right base point)
    bp2_candidates = base_points[base_points[:, 0] == max_x]
    BP2 = bp2_candidates[0] if len(bp2_candidates) > 0 else None
    
    # Find top points
    TP1 = None
    TP2 = None
    
    if BP1 is not None:
        # Find points near BP1's x position
        near_bp1 = points[(np.abs(points[:, 0] - BP1[0]) < 3) & (points[:, 1] < max_y)]
        if len(near_bp1) > 0:
            TP1 = near_bp1[near_bp1[:, 1].argmin()]  # Highest point
    
    if BP2 is not None:
        # Find points near BP2's x position
        near_bp2 = points[(np.abs(points[:, 0] - BP2[0]) < 3) & (points[:, 1] < max_y)]
        if len(near_bp2) > 0:
            TP2 = near_bp2[near_bp2[:, 1].argmin()]  # Highest point
    
    # Calculate heights
    h1 = BP1[1] - TP1[1] if (TP1 is not None and BP1 is not None) else 0
    h2 = BP2[1] - TP2[1] if (TP2 is not None and BP2 is not None) else 0
    
    return (h1, h2)

def digitize_barchart(image_path, x1, y1, x2, y2, p1_value, p2_value):
    """
    Robust bar chart digitization with contour-based height detection
    Args:
        image_path: Path to bar chart image
        x1, y1: Pixel coordinates of baseline reference point
        x2, y2: Pixel coordinates of top reference point
        p1_value: Value at baseline reference point
        p2_value: Value at top reference point
    Returns:
        results: Bar data with values
        output_path: Path to annotated image
    """
    try:
        # Load image and validate
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError("Image not found at provided path")
        
        height, width, _ = img.shape
        
        # Calculate vertical axis position
        vertical_axis_x = int((x1 + x2) / 2)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Define precise ROI using baseline and axis
        buffer = 0
        roi_left = vertical_axis_x + buffer
        roi_right = width - buffer
        roi_top = y2-height
        roi_bottom = y1 + buffer

        #ROI Mask
        roi_mask = np.zeros((height, width), dtype=np.uint8)
        roi_mask[roi_top:roi_bottom, roi_left:roi_right] = 255

          
        # Create histogram of ROI pixel intensities
        roi_pixels = gray[roi_top:roi_bottom, roi_left:roi_right].flatten()
        
        # Handle empty ROI case
        if len(roi_pixels) == 0:
            raise ValueError("ROI is empty - check reference points")
        
        hist, _ = np.histogram(roi_pixels, bins=256, range=(0, 256))
        
        # Find peak intensity (background) and set threshold
        peak_intensity = np.argmax(hist)
        threshold_value = max(0, peak_intensity - 20)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY_INV)
        thresh_roi = cv2.bitwise_and(thresh, roi_mask)
        
        # Morphological processing
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        cleaned = cv2.morphologyEx(thresh_roi, cv2.MORPH_CLOSE, kernel, iterations=3)
        cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(cleaned, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # filter contours for width greater than 10
        contours = [
            cnt for cnt in contours 
            if cv2.boundingRect(cnt)[2] > 10
        ]
        

        # Process contours to form bars with pixel heights 
        bars = []
        for contour in contours:
                           
            h1, h2 = calculate_heights(contour)
            
            # Skip bars with invalid heights
            if h1 <= 0 or h2 <= 0:
                continue
                
            # Get x-range of the contour
            x_coords = contour[:, 0, 0]
            bar_left = np.min(x_coords)
            
            bars.append({
                'x': bar_left,
                'h1': h1,
                'h2': h2
            })
        
        # Sort bars left to right
        bars.sort(key=lambda b: b['x'])
        
        # Calculate scale factor
        pixel_dist = abs(y1 - y2)
        value_diff = p2_value - p1_value
        scale = value_diff / pixel_dist
        
        # Prepare output visualization
        output_img = img.copy()
        cv2.drawContours(output_img, contours, -1, (0, 0, 255), 2)

        # Prepare results 
        results = []
        total1= 0
        total2 = 0
        for i, bar in enumerate(bars):
            # Calculate actual values using the scale factor
            actual_value1 = p1_value + (bar['h1'] * scale)
            actual_value2 = p1_value + (bar['h2'] * scale)
            if actual_value1 == actual_value2:
                actual_value2 = 0
            
            total1 = total1+actual_value1
            total2 = total2+actual_value2
            
            results.append({
                'index': i+1,
                'x': bar['x'],
                'height_pixels1': bar['h1'],
                'height_pixels2': bar['h2'],
                'actual_value1': actual_value1,
                'actual_value2': actual_value2
            })
            
            # # Draw height values on image
            # cv2.putText(output_img, f"H1: {bar['h1']}", (int(bar['x']), 30 + i*30), 
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            # cv2.putText(output_img, f"H2: {bar['h2']}", (int(bar['x']), 60 + i*30), 
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
        # Draw reference system
        cv2.line(output_img, (0, y1), (width, y1), (255, 0, 255), 3)  # Baseline
        cv2.line(output_img, (vertical_axis_x, 0), (vertical_axis_x, height), (0, 0, 255), 2)  # Axis
        cv2.circle(output_img, (x1, y1), 8, (0, 255, 255), -1)  # p1
        cv2.circle(output_img, (x2, y2), 8, (0, 255, 255), -1)  # p2

        # Save output
        output_filename = f"analyzed_{os.path.basename(image_path)}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'analyzed', output_filename)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, output_img)
        
        return results,total1,total2, output_path
        
    except Exception as e:
        # Handle any exceptions and provide meaningful error
        error_msg = f"Error processing image: {str(e)}"
        raise ValueError(error_msg)
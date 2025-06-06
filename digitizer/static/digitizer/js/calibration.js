document.addEventListener('DOMContentLoaded', function() {
    // Canvas setup
    const canvas = document.getElementById('calibration-canvas');
    const ctx = canvas.getContext('2d');
    const helpText = document.getElementById('canvas-help');
    
    // Form elements
    const form = document.getElementById('digitizer-form');
    const imageInput = document.querySelector('[name="original_image"]');
    const x1Input = document.querySelector('[name="x1"]');
    const y1Input = document.querySelector('[name="y1"]');
    const x2Input = document.querySelector('[name="x2"]');
    const y2Input = document.querySelector('[name="y2"]');
    const baselineValue = document.getElementById('baseline-value');
    const resetBtn = document.getElementById('reset-points');
    
    // State variables
    let img = new Image();
    let points = [];
    let scaleFactor = 1;
    let imageOffset = { x: 0, y: 0 };
    
    // Initialize canvas
    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    
    function updateCanvasSize() {
        const container = canvas.parentElement;
        const width = container.clientWidth;
        const height = Math.max(400, width * 0.6);
        
        if (canvas.width !== width || canvas.height !== height) {
            canvas.width = width;
            canvas.height = height;
            drawCanvasBackground();
            redrawImage();
        }
    }
    
    function drawCanvasBackground() {
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        ctx.strokeStyle = '#dee2e6';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        
        // Draw grid
        for (let x = 0; x <= canvas.width; x += 50) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        
        for (let y = 0; y <= canvas.height; y += 50) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }
        
        ctx.setLineDash([]);
    }
    
    function redrawImage() {
        if (!img.src) return;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        imageOffset.x = (canvas.width - img.width * scaleFactor) / 2;
        imageOffset.y = (canvas.height - img.height * scaleFactor) / 2;
        ctx.drawImage(img, imageOffset.x, imageOffset.y, img.width * scaleFactor, img.height * scaleFactor);
        
        // Redraw all points
        points.forEach((point, index) => {
            drawCrosshair(point.screenX, point.screenY, index + 1);
        });
    }
    
    function drawCrosshair(x, y, label) {
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        
        // Horizontal line
        ctx.beginPath();
        ctx.moveTo(x - 15, y);
        ctx.lineTo(x + 15, y);
        ctx.stroke();
        
        // Vertical line
        ctx.beginPath();
        ctx.moveTo(x, y - 15);
        ctx.lineTo(x, y + 15);
        ctx.stroke();
        
        // Label
        ctx.font = 'bold 14px Arial';
        ctx.fillStyle = 'red';
        ctx.fillText(`P${label}`, x + 18, y - 5);
    }
    
    // Handle image upload
    imageInput.addEventListener('change', function(e) {
        if (!e.target.files || !e.target.files[0]) return;
        
        const reader = new FileReader();
        reader.onload = function(event) {
            img.onload = function() {
                helpText.style.display = 'none';
                const maxWidth = canvas.width - 40;
                const maxHeight = canvas.height - 40;
                
                scaleFactor = Math.min(
                    maxWidth / img.width,
                    maxHeight / img.height,
                    1
                );
                
                redrawImage();
                points = [];
                x1Input.value = '';
                y1Input.value = '';
                x2Input.value = '';
                y2Input.value = '';
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(e.target.files[0]);
    });
    
    // Handle canvas clicks
    canvas.addEventListener('click', function(e) {
        if (!img.src) {
            alert('Please upload an image first');
            return;
        }
        
        // Get precise mouse coordinates accounting for canvas CSS scaling
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        
        const mouseX = (e.clientX - rect.left) * scaleX;
        const mouseY = (e.clientY - rect.top) * scaleY;
        
        // Only proceed if clicking within the image area
        if (mouseX < imageOffset.x || mouseX > imageOffset.x + img.width * scaleFactor ||
            mouseY < imageOffset.y || mouseY > imageOffset.y + img.height * scaleFactor) {
            return;
        }
        
        // Draw crosshair at exact click position
        drawCrosshair(mouseX, mouseY, points.length + 1);
        
        // Calculate image coordinates
        const imageCoordX = Math.round((mouseX - imageOffset.x) / scaleFactor);
        const imageCoordY = Math.round((mouseY - imageOffset.y) / scaleFactor);
        
        // Store the point
        points.push({
            screenX: mouseX,
            screenY: mouseY,
            imageX: imageCoordX,
            imageY: imageCoordY
        });
        
        // Update form fields with image coordinates
        if (points.length === 1) {
            x1Input.value = imageCoordX;
            y1Input.value = imageCoordY;
            baselineValue.value = '0.00';
        } else if (points.length === 2) {
            x2Input.value = imageCoordX;
            y2Input.value = imageCoordY;
        }
    });
    
    // Reset points
    resetBtn.addEventListener('click', function() {
        points = [];
        x1Input.value = '';
        y1Input.value = '';
        x2Input.value = '';
        y2Input.value = '';
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        if (img.src) {
            redrawImage();
        } else {
            drawCanvasBackground();
            helpText.style.display = 'block';
        }
    });
    
    // Form validation
    form.addEventListener('submit', function(e) {
        if (points.length < 2) {
            e.preventDefault();
            alert('Please select two calibration points on the y-axis');
        }
    });
});
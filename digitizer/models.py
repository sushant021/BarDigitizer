from django.db import models
from django.contrib.auth.models import User
import os
from django.utils import timezone

def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{timezone.now().strftime("%Y%m%d")}_{filename}'

class BarChartAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField("Analysis Title", max_length=255, default="Untitled Analysis")
    original_image = models.ImageField("Original Image", upload_to=user_directory_path)
    analyzed_image = models.ImageField("Analyzed Image", upload_to='analyzed/', blank=True, null=True)
    x1_position = models.IntegerField("Point 1 X Position",null=True)
    y1_position = models.IntegerField("Point 1 Y Position",null=True)
    x2_position = models.IntegerField("Point 2 X Position",null=True)
    y2_position = models.IntegerField("Point 2 Y Position",null=True)
    p1_value = models.IntegerField(default=0,null=True)
    p2_value = models.IntegerField(null=True)
    # value_difference = models.FloatField("Value Difference")
    created_at = models.DateTimeField("Created At", auto_now_add=True)
    results_json = models.JSONField("Results Data", blank=True, null=True)
    confidence_score = models.FloatField("Confidence Score", default=0.0)

    class Meta:
        verbose_name = "Bar Chart Analysis"
        verbose_name_plural = "Bar Chart Analyses"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def delete(self, *args, **kwargs):
        if self.original_image:
            if os.path.isfile(self.original_image.path):
                os.remove(self.original_image.path)
        if self.analyzed_image:
            if os.path.isfile(self.analyzed_image.path):
                os.remove(self.analyzed_image.path)
        super().delete(*args, **kwargs)
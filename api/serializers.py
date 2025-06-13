from rest_framework import serializers
from digitizer.models import BarChartAnalysis

class BarChartDigitizerSerializer(serializers.Serializer):
    image = serializers.ImageField(write_only=True)
    x1 = serializers.IntegerField(min_value=0)
    y1 = serializers.IntegerField(min_value=0)
    x2 = serializers.IntegerField(min_value=0)
    y2 = serializers.IntegerField(min_value=0)
    p1_value = serializers.IntegerField(default=0)
    p2_value = serializers.IntegerField()

    def validate(self, data):
        # Validate point alignment
        if abs(data['x1'] - data['x2']) > 50:
            raise serializers.ValidationError("Points must be vertically aligned (x-difference ≤ 50px)")
        if abs(data['y1'] - data['y2']) < 10:
            raise serializers.ValidationError("Points must be vertically separated by ≥10px")
        return data
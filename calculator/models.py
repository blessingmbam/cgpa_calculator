import json

from django.db import models
from django.utils import timezone


def default_grade_mapping(scale):
    """Return default grade -> point mapping based on scale."""
    if scale == 4.0:
        return {
            "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0,
            "B-": 2.7, "C+": 2.3, "C": 2.0, "C-": 1.7,
            "D": 1.0, "F": 0.0,
        }
    elif scale == 5.0:
        return {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}
    elif scale == 7.0:
        return {
            "A": 7.0, "B": 6.0, "C": 5.0, "D": 4.0, "E": 3.0,
            "F": 2.0, "G": 1.0, "H": 0.0,
        }
    elif scale == 10.0:
        return {
            "O": 10.0, "A+": 9.0, "A": 8.0, "B+": 7.0,
            "B": 6.0, "C": 5.0, "D": 4.0, "F": 0.0,
        }
    return {"A": 5.0, "B": 4.0, "C": 3.0, "D": 2.0, "E": 1.0, "F": 0.0}


class Settings(models.Model):
    scale = models.FloatField(default=5.0)
    grade_mapping = models.TextField(default='', blank=True)

    class Meta:
        verbose_name_plural = "Settings"

    def __str__(self):
        return f"Settings (scale={self.scale})"

    def get_grade_mapping(self):
        if not self.grade_mapping:
            return default_grade_mapping(self.scale)
        try:
            data = json.loads(self.grade_mapping)
            if isinstance(data, dict) and data:
                return data
        except (ValueError, TypeError):
            pass
        return default_grade_mapping(self.scale)

    def set_grade_mapping(self, mapping):
        self.grade_mapping = json.dumps(mapping)

    @classmethod
    def get_solo(cls):
        """Always return the single settings instance (create if missing)."""
        obj = cls.objects.first()
        if obj is None:
            obj = cls(scale=5.0)
            obj.set_grade_mapping(default_grade_mapping(5.0))
            obj.save()
        return obj


class Semester(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def total_units(self):
        return sum(c.units for c in self.courses.all())

    @property
    def total_points(self):
        return round(sum(c.units * c.grade_point for c in self.courses.all()), 2)

    @property
    def gpa(self):
        tu = self.total_units
        if tu == 0:
            return 0.0
        return round(self.total_points / tu, 2)


class Course(models.Model):
    course_code = models.CharField(max_length=20)
    units = models.IntegerField()
    grade = models.CharField(max_length=5)
    grade_point = models.FloatField()
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, related_name='courses'
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.course_code} ({self.grade})"

    @property
    def quality_points(self):
        return round(self.units * self.grade_point, 2)

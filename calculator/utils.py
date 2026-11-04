from .models import Settings, Course


def get_settings():
    return Settings.get_solo()


def overall_cgpa():
    courses = Course.objects.all()
    total_units = sum(c.units for c in courses)
    total_points = round(sum(c.units * c.grade_point for c in courses), 2)
    cgpa = round(total_points / total_units, 2) if total_units > 0 else 0.0
    return {
        'total_units': total_units,
        'total_points': total_points,
        'cgpa': cgpa,
    }


def recompute_course_points(mapping):
    """Update stored grade_point on all courses based on a mapping."""
    for course in Course.objects.all():
        if course.grade in mapping:
            course.grade_point = mapping[course.grade]
            course.save(update_fields=['grade_point'])

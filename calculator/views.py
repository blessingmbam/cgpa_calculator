import csv
import io
from datetime import datetime

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CourseForm, SemesterForm
from .models import Course, Semester, default_grade_mapping
from .utils import get_settings, overall_cgpa, recompute_course_points


def index(request):
    semesters = Semester.objects.all()
    settings_obj = get_settings()
    overall = overall_cgpa()

    return render(request, 'calculator/index.html', {
        'semesters': semesters,
        'cgpa': overall['cgpa'],
        'total_units': overall['total_units'],
        'scale': settings_obj.scale,
    })


def add_semester(request):
    settings_obj = get_settings()
    mapping = settings_obj.get_grade_mapping()

    if request.method == 'POST':
        form = SemesterForm(request.POST)
        if form.is_valid():
            semester = Semester.objects.create(name=form.cleaned_data['name'].strip())
            messages.success(
                request,
                f'Semester "{semester.name}" created. Now add your courses.'
            )
            return redirect('view_semester', semester_id=semester.id)
        messages.error(request, 'Semester name is required.')
    else:
        form = SemesterForm()

    return render(request, 'calculator/add_semester.html', {
        'form': form,
        'mapping': mapping,
        'scale': settings_obj.scale,
    })


def view_semester(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    settings_obj = get_settings()
    mapping = settings_obj.get_grade_mapping()

    return render(request, 'calculator/view_semester.html', {
        'semester': semester,
        'courses': list(semester.courses.all()),
        'mapping': mapping,
        'scale': settings_obj.scale,
    })


@require_POST
def add_course(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    settings_obj = get_settings()
    mapping = settings_obj.get_grade_mapping()

    form = CourseForm(request.POST, mapping=mapping)

    if not form.is_valid():
        for field, errors in form.errors.items():
            for err in errors:
                messages.error(request, f"{field.replace('_', ' ').title()}: {err}")
        return redirect('view_semester', semester_id=semester.id)

    code = form.cleaned_data['course_code'].strip().upper()
    grade = form.cleaned_data['grade']
    units = form.cleaned_data['units']

    if grade not in mapping:
        messages.error(
            request, f'Invalid grade. Choose from: {", ".join(mapping.keys())}'
        )
        return redirect('view_semester', semester_id=semester.id)

    Course.objects.create(
        course_code=code,
        units=units,
        grade=grade,
        grade_point=mapping[grade],
        semester=semester,
    )
    messages.success(request, f'Course {code} added.')
    return redirect('view_semester', semester_id=semester.id)


@require_POST
def delete_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    semester_id = course.semester_id
    course.delete()
    messages.success(request, 'Course removed.')
    return redirect('view_semester', semester_id=semester_id)


@require_POST
def delete_semester(request, semester_id):
    semester = get_object_or_404(Semester, id=semester_id)
    semester.delete()
    messages.success(request, 'Semester deleted.')
    return redirect('index')


def settings_view(request):
    settings_obj = get_settings()

    if request.method == 'POST':
        action = request.POST.get('action', 'scale')

        if action == 'scale':
            raw = request.POST.get('scale', '5.0')
            try:
                new_scale = float(raw)
            except ValueError:
                messages.error(request, 'Invalid scale value.')
                return redirect('settings')

            if new_scale not in (4.0, 5.0, 7.0, 10.0):
                messages.error(request, 'Scale must be 4.0, 5.0, 7.0, or 10.0.')
                return redirect('settings')

            new_mapping = default_grade_mapping(new_scale)
            settings_obj.scale = new_scale
            settings_obj.set_grade_mapping(new_mapping)
            settings_obj.save()
            recompute_course_points(new_mapping)
            messages.success(request, f'Grade scale updated to {new_scale}.')
            return redirect('settings')

        if action == 'mapping':
            mapping = {}
            grades = request.POST.getlist('grade_name[]')
            points = request.POST.getlist('grade_point[]')
            for g, p in zip(grades, points):
                g = g.strip().upper()
                if not g:
                    continue
                try:
                    mapping[g] = float(p)
                except ValueError:
                    continue

            if not mapping:
                messages.error(request, 'At least one grade mapping is required.')
                return redirect('settings')

            settings_obj.set_grade_mapping(mapping)
            settings_obj.save()
            recompute_course_points(mapping)
            messages.success(request, 'Custom grade mapping saved.')
            return redirect('settings')

        messages.error(request, 'Unknown action.')
        return redirect('settings')

    mapping = settings_obj.get_grade_mapping()
    return render(request, 'calculator/settings.html', {
        'settings': settings_obj,
        'mapping': mapping,
    })


def export_page(request):
    semesters = Semester.objects.order_by('created_at')
    settings_obj = get_settings()
    overall = overall_cgpa()

    return render(request, 'calculator/export.html', {
        'semesters': semesters,
        'cgpa': overall['cgpa'],
        'total_units': overall['total_units'],
        'total_points': overall['total_points'],
        'scale': settings_obj.scale,
        'now': timezone.now(),
    })


def export_csv(request):
    semesters = Semester.objects.order_by('created_at')

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Course Code', 'Units', 'Grade', 'Grade Point',
                     'Quality Points', 'Semester', 'Semester GPA'])

    for s in semesters:
        gpa = s.gpa
        for c in s.courses.all():
            writer.writerow([c.course_code, c.units, c.grade,
                             c.grade_point, c.quality_points,
                             s.name, gpa])

    overall = overall_cgpa()
    writer.writerow([])
    writer.writerow(['Total Units', overall['total_units']])
    writer.writerow(['Total Quality Points', overall['total_points']])
    writer.writerow(['CGPA', overall['cgpa']])

    filename = f'cgpa_report_{datetime.now().strftime("%Y%m%d")}.csv'
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

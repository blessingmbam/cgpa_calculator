from django.test import TestCase
from django.urls import reverse

from .models import Course, Semester, Settings


class CgpaFlowTests(TestCase):
    def test_all_pages_load(self):
        sem = Semester.objects.create(name="Y1S1")
        for name in ['index', 'add_semester', 'settings', 'export_page', 'export_csv']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(
            self.client.get(reverse('view_semester', args=[sem.id])).status_code, 200
        )

    def test_add_course_and_gpa(self):
        sem = Semester.objects.create(name="Y1S1")
        self.client.post(reverse('add_course', args=[sem.id]),
                         {'course_code': 'csc101', 'units': 3, 'grade': 'A'})
        self.client.post(reverse('add_course', args=[sem.id]),
                         {'course_code': 'mth101', 'units': 2, 'grade': 'C'})
        # (3*5 + 2*3) / 5 = 4.2
        self.assertEqual(sem.gpa, 4.2)
        self.assertEqual(Course.objects.first().course_code, 'CSC101')

    def test_invalid_grade_rejected(self):
        sem = Semester.objects.create(name="Y1S1")
        self.client.post(reverse('add_course', args=[sem.id]),
                         {'course_code': 'X', 'units': 3, 'grade': 'Z'})
        self.assertEqual(Course.objects.count(), 0)

    def test_scale_change_recomputes(self):
        sem = Semester.objects.create(name="S")
        self.client.post(reverse('add_course', args=[sem.id]),
                         {'course_code': 'A1', 'units': 2, 'grade': 'A'})
        self.client.post(reverse('settings'), {'action': 'scale', 'scale': '4.0'})
        self.assertEqual(Settings.get_solo().scale, 4.0)
        self.assertEqual(Course.objects.first().grade_point, 4.0)

    def test_custom_mapping_recomputes(self):
        sem = Semester.objects.create(name="S")
        self.client.post(reverse('add_course', args=[sem.id]),
                         {'course_code': 'A1', 'units': 2, 'grade': 'A'})
        self.client.post(reverse('settings'), {
            'action': 'mapping',
            'grade_name[]': ['A', 'B'], 'grade_point[]': ['4.5', '3.5'],
        })
        self.assertEqual(Course.objects.first().grade_point, 4.5)

    def test_delete_cascade(self):
        sem = Semester.objects.create(name="S")
        Course.objects.create(course_code='A', units=1, grade='A',
                              grade_point=5.0, semester=sem)
        self.client.post(reverse('delete_semester', args=[sem.id]))
        self.assertEqual(Course.objects.count(), 0)

    def test_csv_export(self):
        sem = Semester.objects.create(name="S")
        Course.objects.create(course_code='A', units=3, grade='A',
                              grade_point=5.0, semester=sem)
        resp = self.client.get(reverse('export_csv'))
        self.assertIn('text/csv', resp['Content-Type'])
        self.assertIn(b'CGPA,5.0', resp.content)

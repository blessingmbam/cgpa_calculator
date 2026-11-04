from django import forms


class SemesterForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'e.g. Fall 2024',
            'autofocus': 'autofocus',
        })
    )


class CourseForm(forms.Form):
    course_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. CSC101'})
    )
    units = forms.IntegerField(min_value=1, max_value=12)
    grade = forms.CharField(max_length=5)

    def __init__(self, *args, mapping=None, **kwargs):
        super().__init__(*args, **kwargs)
        if mapping:
            self.fields['grade'] = forms.ChoiceField(
                choices=[(g, f"{g} ({p} pts)") for g, p in mapping.items()]
            )

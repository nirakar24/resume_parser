from django import forms

class ResumeForm(forms.Form):
    job_description = forms.CharField(widget=forms.Textarea(attrs={'rows': 6}), label='Job Description')
    resume = forms.FileField(label='Upload Resume (PDF)')

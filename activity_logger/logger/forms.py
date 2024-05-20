from django import forms
from .models import Member, ActivityLog

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name']

class BulkMemberForm(forms.Form):
    names = forms.CharField(widget=forms.Textarea, help_text="이름을 쉼표 또는 줄바꿈으로 구분하여 입력하세요.")

class ActivityLogForm(forms.Form):
    date = forms.CharField(max_length=10)
    activity_name = forms.CharField(max_length=100)
    participants = forms.ModelMultipleChoiceField(
        queryset=Member.objects.all().order_by('name'),
        widget=forms.CheckboxSelectMultiple
    )
    duration = forms.CharField(max_length=20)

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, UserAnalytics

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=True)
        Profile.objects.create(user=user)
        UserAnalytics.objects.create(user=user)
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['dark_mode', 'font_preference']

class ProfileSettingsForm(forms.ModelForm):
    email = forms.EmailField()
    current_password = forms.CharField(widget=forms.PasswordInput, required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Profile
        fields = ['dark_mode']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user:
            self.fields['email'].initial = self.instance.user.email

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password'):
            if not cleaned_data.get('current_password'):
                raise forms.ValidationError('Current password is required')
            if cleaned_data.get('new_password') != cleaned_data.get('confirm_password'):
                raise forms.ValidationError('Passwords do not match')
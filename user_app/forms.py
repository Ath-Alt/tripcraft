from django import forms
from . import models
from django.contrib.auth.models import User

# [Az] create a form
class catForm(forms.ModelForm):
    class Meta:
        model = models.Category
        fields = ['name', 'img', 'color']
    
    name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Enter Category Name',
        'id': 'Category-name'
    }))
    img = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'image', 'hidden': 'hidden'}))
    color = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'id': 'color','type': 'color'}))
# [Az] trip form
class tripForm(forms.ModelForm):
    class Meta:
        model = models.Trip
        fields = ['name', 'destination', 'duration', 'date', 'color', 'img']
        exclude = ['user', 'main_area', 'category']

    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'id': 'trip-name'}))
    destination = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'id':"destination" }))
    duration = forms.IntegerField(
        widget=forms.TextInput(attrs={'class': 'input', 'id':"duration", 'placeholder': "in days"}),
        min_value=1,
        error_messages={'invalid': 'Please enter a valid number of days'})
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'input', 'id': "date", 'type': 'date'}))
    img = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'image', 'hidden': 'hidden'}))
    color = forms.CharField(widget=forms.TextInput(attrs={'class': 'input', 'id': 'color','type': 'color'}))

#[Lyan]
# [Lyan] UserProfile Form for updating avatar, bio, and username
class UserProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=False)

    class Meta:
        model = models.UserProfile
        fields = ['avatar', 'bio']
        widgets = {
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'avatar'}),
            'bio': forms.Textarea(attrs={'class': 'input', 'id': 'bio', 'placeholder': 'Tell us about yourself', 'rows': 4}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and User.objects.filter(username=username).exclude(id=self.instance.user.id).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user = user_profile.user
        username = self.cleaned_data.get('username')
        if username:
            user.username = username
            if commit:
                user.save()
        if commit:
            user_profile.save()
        return user_profile

# [Lyan] Follow Form for adding a follow by username
class FollowForm(forms.Form):
    follow_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': 'Enter username',
            'id': 'follow-username'
        })
    )

    def clean_follow_username(self):
        follow_username = self.cleaned_data.get('follow_username')
        try:
            follow = User.objects.get(username=follow_username)
        except User.DoesNotExist:
            raise forms.ValidationError("User with this username does not exist.")
        return follow
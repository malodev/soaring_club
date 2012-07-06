from django import forms
from models import *

from django.contrib.auth.models import User
from django.forms import ValidationError
from django.utils.translation import ugettext as _



class QuestionForm(forms.Form):
    category = forms.ChoiceField()
    title = forms.CharField(max_length = 300)
    description = forms.CharField(widget = forms.Textarea)    
    def __init__(self, user = None, category = None, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        if category:
            self.fields['category'].choices = ((category.slug, category.name),)
        else:
            categories  = Category.objects.all()
            self.fields['category'].choices = [(category.slug, category.name) for category in categories]
        self.user = user
        
    
    def save(self):
        category = Category.objects.get(slug = self.cleaned_data['category'])
        question = Question(user = self.user, category = category, title =self.cleaned_data['title'], description = self.cleaned_data['description'])
        question.save()
        return question
        
    class Meta:
        model = Question
        exclude = ('user', 'is_open')
    
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('slug')
        
class AnswerForm(forms.Form):
    def __init__(self, user = None, question = None, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)
        self.user = user
        self.question = question
        
    def save(self):
        answer = Answer(text = self.cleaned_data['answer'])
        answer.user = self.user
        answer.question = self.question
        answer.save()
        return answer
    
    answer = forms.CharField(widget = forms.Textarea)
    
class UserCreationForm(forms.Form):
    """A form that creates a user, with no privileges, from the given username and password."""
    username = forms.CharField(max_length = 30, required = True)
    password1 = forms.CharField(max_length = 30, required = True, widget = forms.PasswordInput)
    password2 = forms.CharField(max_length = 30, required = True, widget = forms.PasswordInput)

    def clean_username (self):
        alnum_re = re.compile(r'^\w+$')
        if not alnum_re.search(self.cleaned_data['username']):
            raise ValidationError("This value must contain only letters, numbers and underscores.")
        self.isValidUsername()
        return self.cleaned_data['username']

    def clean (self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise ValidationError(_("The two password fields didn't match."))
        return super(forms.Form, self).clean()
        
    def isValidUsername(self):
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except User.DoesNotExist:
            return
        raise ValidationError(_('A user with that username already exists.'))
    
    def save(self):
        return User.objects.create_user(self.cleaned_data['username'], '', self.cleaned_data['password1'])    
    
class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('best_answers', 'answers', 'points', 'user')
        

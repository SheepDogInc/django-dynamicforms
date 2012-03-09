from django import forms
from dynamicforms.models import DynamicTextQuestion, DynamicResponse
from django.db import models

# Create your models here.

class TextareaQuestion(DynamicTextQuestion):

    @classmethod
    def pretty_name(cls):
        return "Text area question"

    def display(self, user):
        f = forms.CharField(label=self.question_text, widget=forms.Textarea)
        return f, self.get_form_name()


class TextareaQuestion(DynamicResponse):
    text_response = models.TextField()
    question = models.ForeignKey(TextareaQuestion)

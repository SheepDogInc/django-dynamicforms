from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django import forms
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType


QUESTION_TYPES = [
    ('dynamictextquestion', 'Text question',),
    ('dynamicyesnoquestion', 'Yes/No question',),
    ('dynamicmultiplechoicequestion', 'Multiple choice question',),
    ('dynamicratingquestion', 'Rating question',),
]


class InheritanceResolveModel(models.Model):
    """
    An abstract base class that provides a ``real_type`` FK to ContentType.

    For use in trees of inherited models, to be able to downcast
    parent instances to their child types.

    http://stackoverflow.com/questions/929029/how-do-i-access-the-child-classe
    s-of-an-object-in-django-without-knowing-the-name
    """
    real_type = models.ForeignKey(ContentType, editable=False, null=True,
            related_name="%(app_label)s_%(class)s_inheritance_related")

    def save(self, *args, **kwargs):
        if not self.id:
            self.real_type = self._get_real_type()
        super(InheritanceResolveModel, self).save(*args, **kwargs)

    def _get_real_type(self):
        return ContentType.objects.get_for_model(type(self))

    def resolve(self):
        try:
            return self.real_type.get_object_for_this_type(pk=self.pk)
        except AttributeError:
            raise AttributeError(
                "Failed to access real type for %s with self.real_type=%s" %
                    (self, self.real_type))

    class Meta:
        abstract = True


class DynamicForm(models.Model):
    name = models.CharField(max_length=255)
    questions = generic.GenericRelation('DynamicFormQuestion')

    def admin_url(self):
        return '/admin/dynamicforms/dynamicform/%d/' % self.id

    def __unicode__(self):
        return self.name


###############################################################################
# Questions
###############################################################################


class DynamicFormQuestion(InheritanceResolveModel):
    question_text = models.TextField()
    content_type = models.ForeignKey(ContentType, related_name="content_types")
    object_id = models.PositiveIntegerField()
    parent_object = generic.GenericForeignKey('content_type', 'object_id')
    order = models.IntegerField(default=1000)

    class Meta:
        ordering = ['order', 'id']

    def __unicode__(self):
        return "%s..." % self.question_text[:20]

    def admin_url(self):
        return '/admin/dynamicforms/%s/%d/' % (self.real_type.model, self.id)

    def pretty_name(self):
        raise NotImplementedError(
                "You should resolve me first before you ask me my name")

    def display(self, user):
        raise NotImplementedError("I don't know how to display myself.")

    def get_type(self):
        return str(self._get_real_type())

    def get_form_name(self):
        """
        """
        return '%s-%d' % (slugify(self.get_type()), self.id,)


class DynamicTextQuestion(DynamicFormQuestion):

    def pretty_name(self):
        return "Text question"

    def display(self, user):
        f = forms.CharField(label=self.question_text, widget=forms.Textarea)
        return f, self.get_form_name()


class DynamicMultipleChoiceQuestion(DynamicFormQuestion):

    def pretty_name(self):
        return "Multiple choice question"

    def get_choices(self):
        answers = self.dynamicmultiplechoiceanswer_set.all()
        name = 'dynamic-multiple-choice-answer-%d'
        return [(name % a.pk, a.answer_text,) for a in answers]

    def display(self, user):
        f = forms.MultipleChoiceField(label=self.question_text,
                widget=forms.widgets.CheckboxSelectMultiple(),
                choices=self.get_choices())
        return f, self.get_form_name()


class DynamicYesNoQuestion(DynamicMultipleChoiceQuestion):

    def pretty_name(self):
        return "Yes/No question"

    def display(self, user):
        choices = [
            ('yes', 'Yes',),
            ('no', 'No',),
        ]
        f = forms.ChoiceField(label=self.question_text,
                widget=forms.widgets.RadioSelect(),
                choices=choices)
        return f, self.get_form_name()


class DynamicRatingQuestion(DynamicMultipleChoiceQuestion):
    
    def pretty_name(self):
        return "Rating question"

    def get_choices(self):
        answers = self.dynamicratinganswer_set.all()
        name = 'dynamic-rating-answer-%d'
        return [(name % a.pk, a.answer_text,) for a in answers]

    def display(self, user):
        f = forms.ChoiceField(label=self.question_text,
                widget=forms.widgets.RadioSelect(),
                choices=self.get_choices())
        return f, self.get_form_name()


class DynamicMultipleChoiceAnswer(models.Model):
    question = models.ForeignKey(DynamicMultipleChoiceQuestion)
    answer_text = models.TextField()


class DynamicRatingAnswer(models.Model):
    question = models.ForeignKey(DynamicRatingQuestion)
    answer_text = models.TextField()

    def __unicode__(self):
        return self.answer_text

###############################################################################
# Responses
###############################################################################


class DynamicResponseSet(models.Model):
    user = models.ForeignKey(User)
    dynamic_form = models.ForeignKey(DynamicForm)
    added = models.DateTimeField(auto_now_add=True)
    interviewer = models.ForeignKey(User, null=True, related_name="responsesets_as_interviewer")

    def __unicode__(self):
        t = self.added.strftime("%m/%d/%y")
        return "%s' responses to %s (%s)" % (self.user.username,
                self.dynamic_form.name, t)

    @property
    def responses(self):
        return list(list(self.dynamicmultiplechoiceresponse_set.all()) + \
            list(self.dynamictextresponse_set.all()) +
            list(self.dynamicratingresponse_set.all()) + \
            list(self.dynamicyesnoresponse_set.all()))


class DynamicResponse(models.Model):
    user = models.ForeignKey(User)
    submitted = models.DateTimeField(default=datetime.utcnow())
    dynamic_response_set = models.ForeignKey(DynamicResponseSet)

    class Meta:
        abstract = True


class DynamicTextResponse(DynamicResponse):
    text_response = models.TextField()
    question = models.ForeignKey(DynamicTextQuestion)

    def __unicode__(self):
        return self.text_response


class DynamicMultipleChoiceResponse(DynamicResponse):
    question = models.ForeignKey(DynamicMultipleChoiceQuestion)
    answer = models.ForeignKey(DynamicMultipleChoiceAnswer)

    def __unicode__(self):
        return self.answer.answer_text


class DynamicYesNoResponse(DynamicResponse):
    question = models.ForeignKey(DynamicYesNoQuestion)
    response = models.BooleanField()

    def __unicode__(self):
        if self.response:
            return 'Yes'
        else:
            return 'No'


class DynamicRatingResponse(DynamicResponse):
    question = models.ForeignKey(DynamicRatingQuestion)
    response = models.ForeignKey(DynamicRatingAnswer)

    def __unicode__(self):
        return self.response.answer_text

from re import compile
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import models


class DynamicFormShell(forms.Form):
    """
    Used to display front-facing content

    You should never create an instance of this class manually. It's just an
    empty shell that is use dby the DynamicFormCreator class. All fields are
    added to it after an instance is created. See docs on DynamicFormCreator
    for more information on how this works
    """

    def __init__(self, *args, **kwds):
        kwds['label_suffix'] = ''
        return super(DynamicFormShell, self).__init__(*args, **kwds)

    def add_field(self, key, value):
        self.fields[key] = value

    def has_field(self, key):
        return key in self.fields


class DynamicFormCreator(object):

    PATTERN = compile(r'^([a-z-]+)-([0-9]+)$')

    def __init__(self, request, dynamicform_id, redirect=None, user=None,
            force_new_set=False):
        """
        This is the heart of the DynamicForms app. This class creates an
        instance of DynamicFormShell and inserts into it the form fields
        specified via the admin interface. When a POST is requested, it will
        reconstruct the form, validate and save it.

        Arguments:
            `request`         - the request object that the view received
            `dynamicform_id`  - the form that you would like to use
            `redirect`        - redirect url
            `user`            - user override; use logged in user by default
            `force_new_set`   - each time a form is filled out, create new
                                 response set
        """

        self.request = request
        if user:
            self.user = user
        else:
            self.user = self.request.user
        self.dynamicform_id = dynamicform_id
        self.redirect = redirect
        self.force_new_set = force_new_set

        self.dynamicform = get_object_or_404(models.DynamicForm,
                id=self.dynamicform_id)
        self.form = DynamicFormShell()
        self.contents = self.dynamicform.questions.all()

        self.response_set = None
        self.success = False

        self.populate_form()

        if self.request.POST:
            self.add_data(request.POST)
            self.save_data()

    def populate_form(self):
        for item in self.contents:
            item = item.resolve()
            f, id = item.display(self.user)
            self.form.add_field(id, f)

    def get(self):
        return self.form

    def add_data(self, data):
        """
        Add user-submitted data to the form, and mark it as bound
        """
        if data:
            self.form.data = data
            self.form.is_bound = True

    def save_data(self):
        """
        Check if the submitted form was valid and save the data
        """
        if not self.form.is_valid():
            return
        data = self.form.cleaned_data

        if self.force_new_set:
            self.response_set = models.DynamicResponseSet.objects.create(
                    user=self.user,
                    dynamic_form=self.dynamicform,
                    interviewer=self.request.user)
        else:
            self.response_set = \
                models.DynamicResponseSet.objects.get_or_create(
                    user=self.user,
                    dynamic_form=self.dynamicform,
                    interviewer=self.request.user)[0]

        for d in data:
            try:
                meta = self.PATTERN.findall(d)[0]
            except IndexError:
                pass
            response = self.form.cleaned_data[d]
            self._save_response(meta, response)

        self.success = True

        return HttpResponseRedirect(self.redirect)

    def is_success(self):
        return self.success

    def _save_response(self, meta, response):
        """
        Insert the response to the database. This method ensures that no
        prorperly validated responses get thrown away.
        """
        type = meta[0]
        id = meta[1]
        if type == 'dynamic-text-question':
            self._save_text_response(type, id, response)
        elif type == 'dynamic-multiple-choice-question':
            self._save_multiple_choice_question(type, id, response)
        elif type == 'dynamic-yes-no-question':
            self._save_yesno_response(type, id, response)
        elif type == 'dynamic-rating-question':
            self._save_rating_response(type, id, response)
        else:
            raise NotImplementedError(
                    "I don't know how to save this question type.")

    def _save_text_response(self, type, id, response):
        q = models.DynamicTextQuestion.objects.get(id=id)
        models.DynamicTextResponse.objects.create(
            user=self.user,
            question=q,
            dynamic_response_set=self.response_set,
            text_response=response)

    def _save_multiple_choice_question(self, type, id, responses):
        q = models.DynamicMultipleChoiceQuestion.objects.get(id=id)
        if responses:
            for r in responses:
                meta = self.PATTERN.findall(r)[0]
                answer = \
                    models.DynamicMultipleChoiceAnswer.objects.get(id=meta[1])
                models.DynamicMultipleChoiceResponse.objects.create(
                        user=self.user,
                        question=q,
                        dynamic_response_set=self.response_set,
                        answer=answer)

    def _save_yesno_response(self, type, id, response):
        q = models.DynamicYesNoQuestion.objects.get(id=id)
        if response == 'yes':
            v = True
        else:
            v = False
        models.DynamicYesNoResponse.objects.create(user=self.user,
                question=q,
                dynamic_response_set=self.response_set,
                response=v)

    def _save_rating_response(self, type, id, response):
        q = models.DynamicRatingQuestion.objects.get(id=id)
        meta = self.PATTERN.findall(response)[0]
        answer = models.DynamicRatingAnswer.objects.get(id=meta[1])
        models.DynamicRatingResponse.objects.create(
                user=self.user,
                question=q,
                dynamic_response_set=self.response_set,
                response=answer)

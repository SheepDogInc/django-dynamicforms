Extending
=========

It's highly likely that you will need a custom field type. This section will
provide you with information on how to do that.

Your new question type has to inherit from ``DynamicFormQuestion``. You will
want to override the ``pretty_name()`` method. It returns a string that is used
in the admin area to label the question type::

    def pretty_name(self):
        return "Custom question"

Then, your new question has to override the ``display(self, user)`` method. This method
is responsible for creating and returning an instance of a django form field.
For example::

   def display(self, user):
       f = forms.CharField(max_length=200, label=self.question_text)
       return f, self.get_form_name()

As you can see, you have access to the ``question_text`` attribute of the super
class which contains the wording of the question. The ``user`` variable is the
Django ``User`` filling out the form.

Last step is to add your new field to the ``DYNAMICFORMS_CUSTOM_TYPES`` tuple
in your project's ``settings.py``.

Example
-------

This goes in your ``models.py`` file::

    from django import forms
    from dynamicforms.models import DynamicFormQuestion


    class TextareaQuestion(DynamicFormQuestion):

        def pretty_name(self):
            return "Text area question"

        def display(self, user):
            f = forms.CharField(label=self.question_text, widget=forms.Textarea)
            return f, self.get_form_name()

And enable it in your settings::

    DYNAMICFORMS_CUSTOM_TYPES = (
        'project.app.models.TextareaQuestion',
    )

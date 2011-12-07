Extending
=========

It's highly likely that you will need a custom field type. This section will
provide you with information on how to do that.

Your new question type has to inherit from ``DynamicFormQuestion``. You will
want to override the ``pretty_name()`` method::

    def pretty_name(self):
        return "Custom question"

Then, your new question has to override the ``display(self, user)`` method. This method
is responsible for creating and returning an instance of a django form field.
For example::

   def display(self, user):
       f = forms.CharField(max_length=200, label=self.question_text)
       return f, self.get_form_name()

Last step is to add the newly created field to the ``QUESTION_TYPES`` global
variable in ``models.py``.



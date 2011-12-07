API reference
=============

.. class:: DynamicFormCreator

   This is the heart of the application. It takes care of the rendering, saving
   and validation of forms.

.. class:: DynamicFormCreator(request, dynamicform_id[, redirect=None, user=None, force_new_set=False)

   The constructor method. *request* is the django view request object.
   *dynamicform_id* is an ID of the :class:`DynamicForm` instance you want to
   display. Once the form is successfully submitted and saved, redirect to
   *redirect*. By default, we will use the currently logged in user as the
   author of the responses - passing a ``User`` instance to *user* will
   override it. *force_new_set* will make sure that each time the form is saved
   a new bucket is created, otherwise it's overriden.

Instance methods:

.. method:: DynamicFormCreator.get()

   Return an instance of the form. The form is a subclass of ``forms.Form``.

.. method:: DynamicFormCreator.is_success()

    Return ``True`` if the form was sucessfully submitted. Otherwise, return
    ``False``.

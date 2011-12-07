Usage
=====

Installation
------------

* ``pip install dynamicforms``
* Add ``dynamicforms`` to your ``INSTALLED_APPS``
* Enable the Django admin for your project


Views
-----

In your view, you will do something like this::

    from dynamicforms.forms import DynamicFormCreator

    def survey(request, survey_id):
        creator = DynamicFormCreator(request, survey_id, redirect='/done')
        form = creator.get()
        return render_to_response('survey.html', {'form': form})

The ``DynamicFormCreator`` class will take care of creating, saving and
validating your form. If a form was sucessfully saved, the user will be
redirected to the URL specified in ``redirect``.

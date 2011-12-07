Usage
=====

Installation
------------

* Clone this repository into your project's root directory (``git submodule``
  is recommended). No pip support yet.
* Add ``dynamicforms`` into your ``INSTALLED_APPS``
* Make super you enabled admin for your project

Views
-----

In your view, you will do something like this::

    from dynamicforms.forms import DynamicFormCreator

    def index(request):
        creator = DynamicFormCreator(request, form_id, redirect='/done')
        form = creator.get()
        return render_to_response('index.html', {'form': form})

The ``DynamicFormCreator`` class will take care of creating, saving and
validating your form. If a form was sucessfully saved, the user will be
redirected to the URL specified in ``redirect``.

# Django Dynamic Forms

### Motivation

Clients often want to be able to create templates for their forms. Let's say
the company conducts interviews for a large number of positions on a daily
basis. They want to be able to create an interview form for every position.
They would do this quite often because requirements change. It's not practical
to contact the application's developer to add/remove a field from a form each
time a requirement changes. This is where dynamic forms come in. 

Via the django admin interface, clients can create forms and insert into them
whatever fields they want, in whatever order. They can easily reorder
questions, change wording, etc. When the client's end users interact with the
application, they are presented with a simple HTML form. This form is submitted
and responses saved. Each form can be submitted multiple times - each response
to that form will then be saved into a 'bucket' of sorts that holds all the
responses that particular user submitted at that time. This is useful if you
are conducting a periodical survey.

Django dynamic forms comes as a reusable django app that you can easily drop
into your project.

### Installation

* `pip install django-dynamicforms`
* Add `dynamicforms` into your `INSTALLED_APPS`
* Make sure you enabled admin for your project

### Usage

#### Views

In your view, you would do something like this:

    from dynamicforms.forms import DynamicFormCreator

    def index(request):
        creator = DynamicFormCreator(request, form_id, redirect='/done')
        form = creator.get()
        return render_to_response('index.html', {'form': form})

The `DynamicFormCreator` class will take care of creating, saving and
validating your form. If a form was sucessfully saved, the user will be
redirected to the URL specified in `redirect`.

#### Admin

In the django admin, you will automatically see a tab for dynamic forms. You
create a new dynamic form, and then you can questions to the form. You can drag
and drop existing questions to reorder them.


### TODO

* Add question types
* Figure out a way to distribute admin media
* Allow overrides for the user (if someone is filling out the form on a user's
  behalf, e.g. phone interview)
* unittests
* General code clean up

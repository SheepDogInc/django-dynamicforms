from dynamicforms.forms import DynamicFormCreator
from dynamicforms.models import DynamicForm
from django.shortcuts import render_to_response
from django.template import RequestContext


def home(request):
    forms = DynamicForm.objects.all()
    return render_to_response('index.html', {
        'forms': forms
    })


def poll(request, poll_id):
    creator = DynamicFormCreator(request, poll_id, redirect='/done')
    form = creator.get()
    return render_to_response('poll.html', {'form': form},
            context_instance=RequestContext(request))

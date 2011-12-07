from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
import models


def add_dynamicform_to_request(old_view):
    """
    Decorator which alters the request to add dynamicform information to post
    so generic content types know their parent on creation.
    """
    def new_view(cls, request, *args, **kwds):
        dynamicform_id = ContentType.objects.filter(app_label='dynamicforms',
                model='dynamicform').get().id
        if (request.method == 'GET'
            and request.session.get('last_dynamicform_id', None)):
            import copy
            req = copy.copy(request)
            req.GET = request.GET.copy()
            req.GET.setdefault('content_type', dynamicform_id)
            req.GET.setdefault('object_id',
                    request.session.get('last_dynamicform_id'))
        else:
            req = request
        return old_view(cls, req, *args, **kwds)
    return new_view


def redirect_to_last_dynamicform(request):
    dynamicform_id = request.session.get('last_dynamicform_id', None)
    if dynamicform_id:
        dynamicform = models.DynamicForm.objects.get(pk=dynamicform_id)
        return HttpResponseRedirect('/admin/dynamicforms/dynamicform/%d/' %
                dynamicform.id)
    else:
        return '/admin/survey/'


def list_contents_match(l1, l2):
    """
    Return true if and only if l1 and l2 have the same contents, but maybe in
    a different order.
    """
    l1, l2 = (list(l1), list(l2))
    l1.sort()
    l2.sort()
    return l1 == l2

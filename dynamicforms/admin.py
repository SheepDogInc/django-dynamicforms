from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.admin.util import unquote
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
import django.forms
import django.db.models
import models
import views


class ContentCreationForm(django.forms.Form):
    """
    Provides a selector for which type of content to include in a Folder.
    Filters over models in SURVEY_CONTENT_CHOICE_LIST and uses the display
    format defined therein.
    """
    choices = models.CHOICES
    new_content_type = django.forms.ChoiceField(choices=choices)


class DynamicFormAdminForm(django.forms.ModelForm):
    class Meta:
        model = models.DynamicForm


class DynamicFormAdmin(admin.ModelAdmin):
    """
    When adding content to a dynamicform, we do it by first creating and
    saving the content object, and then allowing edit of the empty shell.
    This gets around the problem of having to inject initialization info into
    the Django's admin for the object creation The problem, of course, is that
    the model can't have required fields AND if the user change's his mind, he
    will find a blank object he'll have to delete.
    """
    form = DynamicFormAdminForm
    change_form_template = "admin/change_dynamicform.html"
    add_form_template = "admin/add_dynamicform.html"

    def change_view(self, request, object_id, extra_context=None,
            *args, **kwds):
        request.session['last_dynamicform_id'] = object_id
        parent = self.get_object(request, unquote(object_id))
        children = parent.questions.all()
        # Handle the case where someone re-orders the list of content.
        order = [int(x) for x in request.GET.getlist('contentorder[]')]
        if order:
            # Check that the elements in the dynamicform are those in
            # the request
            if views.list_contents_match(order, \
                    [child.pk for child in children]):
                new_assignment = dict(
                    [(order[i], i) for i in range(len(order))])
                for child in children:
                    child.order = 1 + new_assignment[child.pk]
                    child.save()
            # Handle different save buttons being clicked
            if request.POST.get('_continue') is not None:
                return HttpResponseRedirect(parent.admin_url())
            if request.POST.get('_save') is not None:
                return HttpResponseRedirect('/admin/dynamicforms/dynamicform/')
            if request.POST.get('_addanother') is not None:
                return HttpResponseRedirect(
                    '/admin/dynamicforms/dynamicform/add/')
        # Delete selected objects.
        if request.method == 'POST' and \
            request.POST.get('action', None) == 'delete_selected':
            # children as a dict indexed by pk.  That makes sure we only
            # deleted children of current dynamicform
            children = dict([(child.pk, child) for child in children])
            lst = [int(x) for x in request.POST.getlist('_selected_action')]
            n = 0
            for pk in lst:
                child = children.get(pk, None)
                if child:
                    children[pk].delete()
                    n += 1
            from django.utils.translation import ngettext
            self.message_user(request, _("Successfully deleted %d %s.") %
                    (n, ngettext("item", "items", n)))
            return HttpResponseRedirect("")
        context = {'add_content_form': ContentCreationForm(),
                   'contents': children}
        context.update(extra_context or {})
        return super(DynamicFormAdmin, self).change_view(request, object_id,
                extra_context=context, *args, **kwds)

    def _actions_column(self, dynamicform):
        a = '<a title="Preview" href="%s" target="_blank"><img alt="Preview" src="/media/img/preview.gif" /></a>&nbsp;' % dynamicform.admin_url('preview')
        b = '<a title="Copy" href="%s"><img alt="Copy" src="/media/img/copy.png" /></a>&nbsp;' % dynamicform.admin_url('copy')
        return [a, b] + super(DynamicFormAdmin, self)._actions_column(dynamicform)


admin.site.register(models.DynamicForm, DynamicFormAdmin)


class DynamicFormQuestionAdmin(admin.ModelAdmin):
    exclude = ['order']
    change_form_template = "admin/change_question.html"

    @views.add_dynamicform_to_request
    def add_view(self, request, extra_context=None, **kwds):
        dynamicform_id = request.session.get('last_dynamicform_id', None)
        if not dynamicform_id:
            self.message_user(request,
                _("Sorry; please reselect the form before adding content"))
            return HttpResponseRedirect('/admin/dynamicforms/dynamicform/')
        else:
            context = {
                'dynamicform': models.DynamicForm.objects.get(pk=dynamicform_id)
            }
            context.update(extra_context or {})
            return super(DynamicFormQuestionAdmin, self).add_view(request,
                    extra_context=context, **kwds)

    def changelist_view(self, request, *args, **kwds):
        return views.redirect_to_last_dynamicform(request)


###############################################################################
# Responses
###############################################################################

admin.site.register(models.DynamicTextResponse)
admin.site.register(models.DynamicMultipleChoiceResponse)
admin.site.register(models.DynamicMultipleChoiceAnswer)
admin.site.register(models.DynamicResponseSet)
admin.site.register(models.DynamicYesNoResponse)
admin.site.register(models.DynamicRatingResponse)

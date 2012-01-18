from django.contrib import admin
from reversion.admin import VersionAdmin
from django.contrib.admin.filterspecs import FilterSpec
from django.db import models
from django import forms

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response

import logging

from bibliography.models import Reference, Resource

#class UpdatedFilterSpec(FilterSpec):
#    def __init__(self, f, request, params, model, model_admin, field_path=None):
#        super(UpdatedFilterSpec, self).__init__(f, request, params, model, model_admin)
#        if isinstance(f, models.ManyToManyField):
#            self.lookup_title = f.rel.to._meta.verbose_name
#        else:
#            self.lookup_title = f.verbose_name
#        self.null_lookup_kwarg = '%s__isnull' % f.name
#        self.null_lookup_val = request.GET.get(self.null_lookup_kwarg, None)
#        rel_name = f.rel.get_related_field().name
#        self.lookup_kwarg = '%s__%s__exact' % (f.name, rel_name)
#        self.lookup_val = request.GET.get(self.lookup_kwarg, None)
#        self.lookup_choices = f.get_choices(include_blank=False)
#
#    def title(self):
#        return self.lookup_title
#
#    def choices(self, cl):
#        yield {'selected': self.lookup_val is None and self.null_lookup_val is None,
#               'query_string': cl.get_query_string({}, [self.lookup_kwarg,self.null_lookup_kwarg]),
#               'display': ('All')}
#        yield {'selected': self.lookup_val is None and self.null_lookup_val=="True",
#               'query_string': cl.get_query_string({self.null_lookup_kwarg:True},[self.lookup_kwarg]),
#               'display': ('Current')}
#        yield {'selected': self.lookup_val is None and self.null_lookup_val=="False",
#               'query_string': cl.get_query_string({self.null_lookup_kwarg:False},[self.lookup_kwarg]),
#               'display': ('Previous versions')}
#
#FilterSpec.filter_specs.insert(0, (lambda f: f.name == 'updated', UpdatedFilterSpec))
#

class ResourceInline(admin.TabularInline):
    model = Resource
    extra = 0

class ReferenceForm(forms.ModelForm):
    bibtex = forms.CharField(widget = forms.Textarea(attrs={'cols':'100','rows':'20'}))
    def __init__(self, *args, **kwargs):
        super(ReferenceForm, self).__init__(*args, **kwargs)
        self.fields['tags'].widget.attrs['size']='120'
    class Meta:
        model = Reference    

class ReferenceAdmin(VersionAdmin):
    list_display = ('name', 'the_tags', 'year', 'reference', 'with_resources')
    search_fields = ('bibtex',)
    save_on_top = True
    form = ReferenceForm
    list_filter = ('year', 'tags__name')
    readonly_fields = ('name', 'year', 'reference', 'abstract', 'doi')
    inlines = [ResourceInline,]
    actions = ['remove_tags', 'add_tag_edward', 'add_tag_finlay', 'add_tag_yvan', 'add_tag_seabird_bycatch', 'add_tag_habitat_fragmentation','get_tags_from_keywords', 'get_bibtex']
    
    def parent(self, obj):
        return '<a href="%s">Previous version</a>' % obj.parent.get_absolute_url() if obj.parent else ''
    parent.allow_tags=True
    def reference(self, obj):
        return obj.html
    reference.allow_tags=True

    def add_tag_edward(self, request, queryset):
        for ref in queryset:
            ref.tags.add('edward-abraham')
    add_tag_edward.short_description = "Add tag edward-abraham"
    def add_tag_finlay(self, request, queryset):
        for ref in queryset:
            ref.tags.add('finlay-thompson')
    add_tag_finlay.short_description = "Add tag finlay-thompson"
    def add_tag_yvan(self, request, queryset):
        for ref in queryset:
            ref.tags.add('yvan-richard')
    add_tag_yvan.short_description = "Add tag yvan-richard"    
    def add_tag_seabird_bycatch(self, request, queryset):
        for ref in queryset:
            ref.tags.add('seabird-bycatch')
    add_tag_seabird_bycatch.short_description = "Add tag seabird-bycatch"
    def add_tag_habitat_fragmentation(self, request, queryset):
        for ref in queryset:
            ref.tags.add('habitat-fragmentation')
    add_tag_habitat_fragmentation.short_description = "Add tag habitat-fragmentation"
    def remove_tags(self, request, queryset):
        for ref in queryset:
            ref.tags.clear()
    remove_tags.short_description = "Remove tags"
    def get_tags_from_keywords(self, request, queryset):
        for ref in queryset:
            ref.get_keywords()
    get_tags_from_keywords.short_description = "Get tags from keywords"

    def get_bibtex(self, request, queryset):
        bibs = []
        for ref in queryset:
            bibs.append(ref.bibtex)
        bib = '\n\n'.join(bibs)
        return render_to_response('references/bib.bib', dict(bib = bib), mimetype='text/plain')
    get_bibtex.short_description = "Get bibtex content"
            

admin.site.register(Reference, ReferenceAdmin)


class ResourceAdmin(VersionAdmin):
    list_display = ('title','url','file')
admin.site.register(Resource, ResourceAdmin)


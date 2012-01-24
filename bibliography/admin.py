from django.contrib import admin
from reversion.admin import VersionAdmin
from django.contrib.admin.filterspecs import FilterSpec
from django.db import models
from django import forms

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response

import logging

from bibliography.models import Reference, Resource

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
    list_display = ('key', 'the_tags', 'year', 'reference', 'with_resources')
    search_fields = ('bibtex',)
    save_on_top = True
    form = ReferenceForm
    list_filter = ('year', 'tags__name')
    readonly_fields = ('key', 'year', 'reference', 'abstract', 'doi')
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


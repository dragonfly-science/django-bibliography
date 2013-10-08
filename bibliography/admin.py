from django.contrib import admin
from django import forms
from django.shortcuts import render_to_response
from django.conf import settings

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


class ReferenceAdmin(admin.ModelAdmin):
    list_display = ('key', 'the_tags', 'year', 'reference', 'with_resources')
    search_fields = ('bibtex',)
    save_on_top = True
    form = ReferenceForm
    list_filter = ('year', 'tags__name')
    readonly_fields = ('key', 'year', 'reference', 'abstract', 'doi')
    inlines = [ResourceInline,]

    actions = ['remove_tags', 'get_tags_from_keywords', 'get_bibtex']

    def parent(self, obj):
        return '<a href="%s">Previous version</a>' % obj.parent.get_absolute_url() if obj.parent else ''
    parent.allow_tags=True

    def reference(self, obj):
        return obj.html
    reference.allow_tags=True

    def get_actions(self, request):
        actions = super(ReferenceAdmin, self).get_actions(request)

        # Dynamically create tag actions from settings file.
        # TODO: Automatically generate per user tags?
        def make_action(tag_name):
            name = 'add_tag_%s' % tag_name
            def action(modeladmin, req, queryset):
                for ref in queryset:
                    ref.tags.add(tag_name)
            return (name, (action, name, "Add tag %s" % tag_name))

        tags = getattr(settings, 'BIBLIOGRAPHY_TAGS' , [])
        dynamic_actions = []
        for t in tags:
            dynamic_actions.append(make_action(t))

        actions.update(dict(dynamic_actions))
        return actions

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


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('title','url','file')
admin.site.register(Resource, ResourceAdmin)


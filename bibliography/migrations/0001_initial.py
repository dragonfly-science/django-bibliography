# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.SlugField(editable=False)),
                ('bibtex', models.TextField()),
                ('year', models.IntegerField(null=True, editable=False, blank=True)),
                ('html', models.TextField(editable=False)),
                ('sort', models.TextField(null=True, editable=False, blank=True)),
                ('authors', models.TextField(null=True, blank=True)),
                ('title', models.TextField(null=True, editable=False, blank=True)),
                ('abstract', models.TextField(null=True, editable=False, blank=True)),
                ('doi', models.TextField(null=True, editable=False, blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'ordering': ('sort', '-year', 'key'),
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(max_length=256, null=True, upload_to=b'resources', blank=True)),
                ('url', models.URLField(null=True, blank=True)),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('list_title', models.CharField(max_length=255, null=True, blank=True)),
                ('pos', models.IntegerField(null=True, blank=True)),
                ('reference', models.ForeignKey(to='bibliography.Reference')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='reference',
            unique_together=set([('key',)]),
        ),
    ]

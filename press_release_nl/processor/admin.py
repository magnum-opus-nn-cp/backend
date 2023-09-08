from django.contrib import admin

from press_release_nl.processor.models import Entry, Text

admin.site.register(Text)
admin.site.register(Entry)

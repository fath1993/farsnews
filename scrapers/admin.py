from django.contrib import admin

from scrapers.models import FarsNews


@admin.register(FarsNews)
class FarsNewsAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'date',
        'created_at',
    )

    readonly_fields = (
        'created_at',
    )

    fields = (
        'title',
        'sub_title',
        'link_of_content',
        'content',
        'date',
        'created_at',
    )
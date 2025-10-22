from django.contrib import admin
from .models import ScrapeJob, ScrapedData, ScrapeLog


@admin.register(ScrapeJob)
class ScrapeJobAdmin(admin.ModelAdmin):
    list_display = ("id", "url", "status", "scraper_type", "created_at", "completed_at", "total_items_scraped")
    list_filter = ("status", "scraper_type", "created_at")
    search_fields = ("url", "user_instructions", "error_message")
    readonly_fields = ("scraped_data", "error_message", "execution_time", "started_at", "completed_at", "created_at")
    ordering = ("-created_at",)


@admin.register(ScrapedData)
class ScrapedDataAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "scraped_at")
    list_filter = ("scraped_at",)
    search_fields = ("data",)
    readonly_fields = ("scraped_at",)
    ordering = ("-scraped_at",)


@admin.register(ScrapeLog)
class ScrapeLogAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "level", "timestamp", "short_message")
    list_filter = ("level", "timestamp")
    search_fields = ("message",)
    readonly_fields = ("timestamp",)
    ordering = ("timestamp",)

    def short_message(self, obj):
        return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
    short_message.short_description = "Message Preview"

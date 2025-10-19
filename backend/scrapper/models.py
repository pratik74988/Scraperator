
# Create your models here.
from django.db import models
from django.utils import timezone
import json

class ScrapeJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    SCRAPER_TYPE_CHOICES = [
        ('beautifulsoup', 'BeautifulSoup'),
        ('selenium', 'Selenium'),
        ('auto', 'Auto-detect'),
    ]
    
    url = models.URLField(max_length=2000)
    user_instructions = models.TextField(
        help_text="Natural language instructions for what to scrape"
    )
    scraper_type = models.CharField(
        max_length=20,
        choices=SCRAPER_TYPE_CHOICES,
        default='auto'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Results
    scraped_data = models.JSONField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Stats
    total_items_scraped = models.IntegerField(default=0)
    execution_time = models.FloatField(null=True, blank=True, help_text="Time in seconds")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Job #{self.id} - {self.url[:50]} - {self.status}"
    
    def mark_running(self):
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()
    
    def mark_completed(self, data, items_count):
        self.status = 'completed'
        self.scraped_data = data
        self.total_items_scraped = items_count
        self.completed_at = timezone.now()
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
        self.save()
    
    def mark_failed(self, error_msg):
        self.status = 'failed'
        self.error_message = error_msg
        self.completed_at = timezone.now()
        if self.started_at:
            self.execution_time = (self.completed_at - self.started_at).total_seconds()
        self.save()


class ScrapedData(models.Model):
    """Store individual scraped items for better querying"""
    job = models.ForeignKey(ScrapeJob, on_delete=models.CASCADE, related_name='items')
    data = models.JSONField()
    scraped_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['job', '-scraped_at']),
        ]
    
    def __str__(self):
        return f"Data from Job #{self.job.id}"


class ScrapeLog(models.Model):
    """Detailed logs for debugging"""
    LOG_LEVEL_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    
    job = models.ForeignKey(ScrapeJob, on_delete=models.CASCADE, related_name='logs')
    level = models.CharField(max_length=10, choices=LOG_LEVEL_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"[{self.level.upper()}] Job #{self.job.id} - {self.message[:50]}"
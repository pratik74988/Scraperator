from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.http import JsonResponse
from .models import ScrapeJob, ScrapedData, ScrapeLog
from .scraper import AutoScraper, ScrapperException
from rest_framework import serializers
import logging

logger = logging.getLogger(__name__)


# Serializers
class ScrapeJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeJob
        fields = [
            'id', 'url', 'user_instructions', 'scraper_type', 'status',
            'scraped_data', 'error_message', 'created_at', 'started_at',
            'completed_at', 'total_items_scraped', 'execution_time'
        ]
        read_only_fields = [
            'id', 'status', 'scraped_data', 'error_message',
            'created_at', 'started_at', 'completed_at',
            'total_items_scraped', 'execution_time'
        ]


class ScrapeJobCreateSerializer(serializers.Serializer):
    url = serializers.URLField(required=True)
    user_instructions = serializers.CharField(required=False, allow_blank=True)
    scraper_type = serializers.ChoiceField(
        choices=['beautifulsoup', 'selenium', 'auto'],
        default='auto'
    )


class ScrapedDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapedData
        fields = ['id', 'data', 'scraped_at']


class ScrapeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapeLog
        fields = ['id', 'level', 'message', 'timestamp']


# ViewSet
class ScrapeJobViewSet(viewsets.ModelViewSet):
    queryset = ScrapeJob.objects.all()
    serializer_class = ScrapeJobSerializer
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ScrapeJobCreateSerializer
        return ScrapeJobSerializer
    
    def create(self, request):
        """Create a new scrape job"""
        serializer = ScrapeJobCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        url = serializer.validated_data['url']
        user_instructions = serializer.validated_data.get('user_instructions', '')
        scraper_type = serializer.validated_data.get('scraper_type', 'auto')
        
        # Create job
        job = ScrapeJob.objects.create(
            url=url,
            user_instructions=user_instructions,
            scraper_type=scraper_type
        )
        
        # Log creation
        ScrapeLog.objects.create(
            job=job,
            level='info',
            message=f'Job created for URL: {url}'
        )
        
        # Execute scraping immediately (will move to Celery later)
        try:
            job.mark_running()
            ScrapeLog.objects.create(
                job=job,
                level='info',
                message=f'Starting scrape with {scraper_type} scraper'
            )
            
            # Scrape the URL
            data = AutoScraper.scrape(url, scraper_type)
            
            # Count items
            items_count = len(data.get('links', [])) + len(data.get('images', []))
            
            # Mark completed
            job.mark_completed(data, items_count)
            ScrapeLog.objects.create(
                job=job,
                level='info',
                message=f'Scrape completed successfully. Items: {items_count}'
            )
            
        except ScrapperException as e:
            job.mark_failed(str(e))
            ScrapeLog.objects.create(
                job=job,
                level='error',
                message=f'Scrape failed: {str(e)}'
            )
        except Exception as e:
            logger.exception("Unexpected error during scraping")
            job.mark_failed(f"Unexpected error: {str(e)}")
            ScrapeLog.objects.create(
                job=job,
                level='error',
                message=f'Unexpected error: {str(e)}'
            )
        
        # Return updated job
        return Response(
            ScrapeJobSerializer(job).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get logs for a specific job"""
        job = self.get_object()
        logs = job.logs.all()
        serializer = ScrapeLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        """Get scraped items for a specific job"""
        job = self.get_object()
        items = job.items.all()
        serializer = ScrapedDataSerializer(items, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall statistics"""
        total_jobs = ScrapeJob.objects.count()
        completed = ScrapeJob.objects.filter(status='completed').count()
        failed = ScrapeJob.objects.filter(status='failed').count()
        running = ScrapeJob.objects.filter(status='running').count()
        
        return Response({
            'total_jobs': total_jobs,
            'completed': completed,
            'failed': failed,
            'running': running,
            'success_rate': round((completed / total_jobs * 100) if total_jobs > 0 else 0, 2)
        })


# Template Views for Frontend
def dashboard_view(request):
    """Main dashboard view"""
    jobs = ScrapeJob.objects.all()[:10]
    
    # Calculate stats
    total_jobs = ScrapeJob.objects.count()
    completed = ScrapeJob.objects.filter(status='completed').count()
    failed = ScrapeJob.objects.filter(status='failed').count()
    
    context = {
        'jobs': jobs,
        'total_jobs': total_jobs,
        'completed': completed,
        'failed': failed,
    }
    return render(request, 'scraper/dashboard.html', context)


def job_detail_view(request, job_id):
    """Job detail view"""
    try:
        job = ScrapeJob.objects.get(id=job_id)
        logs = job.logs.all()
        
        context = {
            'job': job,
            'logs': logs,
        }
        return render(request, 'scraper/job_detail.html', context)
    except ScrapeJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)


def create_job_view(request):
    """Create new scrape job view"""
    return render(request, 'scraper/create_job.html')
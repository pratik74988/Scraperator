from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render
from django.http import JsonResponse
from .models import ScrapeJob, ScrapedData, ScrapeLog
from .scraper import AutoScraper, ScrapperException
from .agent import AgentManager
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
        """Create a new scrape job with AI processing"""
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
        
        # Execute scraping and AI processing
        try:
            job.mark_running()
            ScrapeLog.objects.create(
                job=job,
                level='info',
                message=f'Starting intelligent scrape with {scraper_type} scraper'
            )
            
            # Use AgentManager for scraping + AI processing
            result = AgentManager.scrape_and_process(
                url=url,
                user_instructions=user_instructions,
                scraper_type=scraper_type
            )
            
            if result['status'] == 'success':
                # Prepare final data
                final_data = {
                    'raw_data': result['raw_data'],
                    'ai_extracted': result.get('ai_processed_data')
                }
                
                # Count items
                items_count = len(result['raw_data'].get('links', [])) + len(result['raw_data'].get('images', []))
                
                # Mark completed
                job.mark_completed(final_data, items_count)
                
                if result.get('ai_processed_data'):
                    ScrapeLog.objects.create(
                        job=job,
                        level='info',
                        message=f'AI processing completed. Extracted structured data based on instructions.'
                    )
                
                ScrapeLog.objects.create(
                    job=job,
                    level='info',
                    message=f'Scrape completed successfully. Items: {items_count}'
                )
            else:
                job.mark_failed(result['error'])
                ScrapeLog.objects.create(
                    job=job,
                    level='error',
                    message=f'Scrape failed: {result["error"]}'
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
    
    @action(detail=False, methods=['post'])
    def ask_question(self, request):
        """Ask a question about a URL without creating a full job"""
        url = request.data.get('url')
        question = request.data.get('question')
        scraper_type = request.data.get('scraper_type', 'auto')
        
        if not url or not question:
            return Response(
                {'error': 'Both url and question are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = AgentManager.answer_question_about_url(url, question, scraper_type)
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def get_suggestions(self, request):
        """Get AI suggestions for what can be extracted from a URL"""
        url = request.data.get('url')
        scraper_type = request.data.get('scraper_type', 'auto')
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = AgentManager.get_extraction_suggestions(url, scraper_type)
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def ask_question(self, request):
        """Ask a question about a URL without creating a full job"""
        url = request.data.get('url')
        question = request.data.get('question')
        scraper_type = request.data.get('scraper_type', 'auto')
        
        if not url or not question:
            return Response(
                {'error': 'Both url and question are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = AgentManager.answer_question_about_url(url, question, scraper_type)
        return Response(result)
    
    @action(detail=False, methods=['post'])
    def get_suggestions(self, request):
        """Get AI suggestions for what can be extracted from a URL"""
        url = request.data.get('url')
        scraper_type = request.data.get('scraper_type', 'auto')
        
        if not url:
            return Response(
                {'error': 'URL is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = AgentManager.get_extraction_suggestions(url, scraper_type)

        # ✅ Fixed: proper single Response() with all fields
        total_jobs = ScrapeJob.objects.count()
        completed = ScrapeJob.objects.filter(status='completed').count()
        failed = ScrapeJob.objects.filter(status='failed').count()
        running = ScrapeJob.objects.filter(status='running').count()

        return Response({
            'result': result,
            'total_jobs': total_jobs,
            'completed': completed,
            'failed': failed,
            'running': running,
            'success_rate': round((completed / total_jobs * 100) if total_jobs > 0 else 0, 2),
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


def ai_test_view(request):
    """AI testing interface"""
    return render(request, 'scraper/ai_test.html')
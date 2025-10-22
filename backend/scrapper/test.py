import json
from models import ScrapeJob
import os 
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config")  # or your actual settings path
django.setup()

job = ScrapeJob.objects.last()  # or filter to the one you want
data = job.scraped_data.get("ai_extracted")
print("Raw data:", data)
try:
    json.loads(data)
    print("✅ It's valid JSON")
except json.JSONDecodeError as e:
    print("❌ Not valid JSON:", e)
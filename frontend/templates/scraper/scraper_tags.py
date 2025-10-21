from django import template

register = template.Library()

@register.filter(name='status_icon')
def status_icon(status):
    """Return Font Awesome icon for job status"""
    icons = {
        'completed': 'check',
        'failed': 'times',
        'running': 'spinner fa-spin',
        'pending': 'clock'
    }
    return icons.get(status, 'question')
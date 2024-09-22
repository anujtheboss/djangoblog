from .models import Website

def website_list(request):
    websites = Website.objects.all()
    website_count = websites.count()
    return {
        'websites': websites,
        'website_count': website_count,
    }

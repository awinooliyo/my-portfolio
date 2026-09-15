from .models import SiteConfig


def site_config(request):
    try:
        config = SiteConfig.objects.get(pk=1)
    except SiteConfig.DoesNotExist:
        config = None
    return {"site_config": config}

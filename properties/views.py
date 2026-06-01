from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import viewsets, permissions
from .models import Property, City, Sublocation
from .serializers import CitySerializer, SublocationSerializer
try:
    from core.models import JobOpening, TeamMember
except ImportError:
    JobOpening = None
    TeamMember = None

class CityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]

class SublocationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SublocationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Sublocation.objects.all()
        city_slug = self.request.query_params.get('city', None)
        if city_slug:
            if city_slug.isdigit():
                queryset = queryset.filter(city_id=city_slug)
            else:
                queryset = queryset.filter(city__slug=city_slug)
        return queryset

def home(request):
    featured_properties = Property.objects.filter(status='published', is_featured=True)[:3]
    latest_properties = Property.objects.filter(status='published').order_by('-created_at')[:3]
    featured_cities = City.objects.filter(is_featured=True)
    return render(request, 'home.html', {
        'featured_properties': featured_properties,
        'latest_properties': latest_properties,
        'featured_cities': featured_cities
    })

def property_list(request):
    # Get all published properties
    properties = Property.objects.filter(status='published')
    
    # Proper city and sub-location filtering
    city_slug = request.GET.get('city', '')
    sublocation_slug = request.GET.get('sublocation', '')

    if city_slug:
        properties = properties.filter(city__slug=city_slug)
    
    if sublocation_slug:
        properties = properties.filter(sublocation__slug=sublocation_slug)
    
    # Search functionality
    search_query = request.GET.get('q')
    if search_query:
        properties = properties.filter(
            Q(title__icontains=search_query) |
            Q(sublocation__name__icontains=search_query) |
            Q(address__icontains=search_query) |
            Q(city__name__icontains=search_query)
        )
    
    # Filter by property type
    property_type = request.GET.get('type')
    if property_type:
        properties = properties.filter(property_type=property_type)
    
    # Filter by bedrooms
    bedrooms = request.GET.get('bedrooms')
    if bedrooms:
        if bedrooms == '4':
            properties = properties.filter(bedrooms__gte=4)
        else:
            properties = properties.filter(bedrooms=bedrooms)
    
    # Filter by price range
    min_price = request.GET.get('min_price')
    if min_price:
        properties = properties.filter(price__gte=min_price)
    
    max_price = request.GET.get('max_price')
    if max_price:
        properties = properties.filter(price__lte=max_price)
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    allowed_sorts = ['price', '-price', 'area_sqft', '-area_sqft', 'created_at', '-created_at']
    if sort_by in allowed_sorts:
        properties = properties.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(properties, 12)  # Show 12 properties per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get cities and sublocations for filter
    all_cities = City.objects.all()
    sublocations = []
    if city_slug:
        sublocations = Sublocation.objects.filter(city__slug=city_slug)
    
    context = {
        'properties': page_obj,
        'search_query': search_query,
        'selected_city': city_slug,
        'selected_sublocation': sublocation_slug,
        'selected_type': property_type,
        'selected_bedrooms': bedrooms,
        'selected_sort': sort_by,
        'min_price': min_price,
        'max_price': max_price,
        'cities': all_cities,
        'sublocations': sublocations,
        'property_types': Property.PROPERTY_TYPES,
    }
    return render(request, 'properties/property_list.html', context)

def property_detail(request, slug):
    property = get_object_or_404(
        Property.objects.select_related('city', 'sublocation', 'builder').prefetch_related('configurations', 'amenities', 'gallery'), 
        slug=slug, 
        status='published'
    )
    
    # Increment view count
    property.views_count += 1
    property.save(update_fields=['views_count'])
    
    # Get similar properties
    similar_properties = Property.objects.filter(
        status='published',
        property_type=property.property_type
    ).exclude(id=property.id)[:4]
    
    context = {
        'property': property,
        'similar_properties': similar_properties,
    }
    return render(request, 'properties/property_detail.html', context)

def about(request):
    team_members = TeamMember.objects.all()
    return render(request, 'about.html', {'team_members': team_members})

def contact(request):
    return render(request, 'contact.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_of_service(request):
    return render(request, 'terms_of_service.html')

def faq(request):
    return render(request, 'faq.html')

def careers(request):
    jobs = JobOpening.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'careers.html', {'jobs': jobs})

def thank_you(request):
    return render(request, 'thank_you.html')

def newsletter_subscribe(request):
    # Placeholder for subscription logic
    return JsonResponse({'status': 'success', 'message': 'Subscribed!'})

def happy_families(request):
    """View to display happy families/testimonials"""
    # Get all published properties that have testimonials
    # You can customize this query based on your actual model structure
    properties_with_testimonials = Property.objects.filter(
        status='published',
        # If you have a testimonials field or related model, add it here
        # For now, just get featured properties
    ).order_by('-created_at')[:12]
    
    return render(request, 'happy_families.html', {
        'properties': properties_with_testimonials,
    })
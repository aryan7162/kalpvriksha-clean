from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .models import Lead, NewsletterSubscriber
from properties.models import Property

def lead_capture(request):
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name', '')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message')
        property_id = request.POST.get('property')
        portfolio_link = request.POST.get('portfolio_link')
        
        if portfolio_link:
            message = f"{message}\n\nPortfolio/LinkedIn: {portfolio_link}"
        configuration = request.POST.get('configuration', '')
        
        # Get IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        # Get user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create lead
        lead = Lead.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            message=message,
            ip_address=ip_address,
            user_agent=user_agent,
            referring_url=request.META.get('HTTP_REFERER', ''),
            source='property_page' if property_id else 'contact_form',
            preferred_property_type=configuration
        )
        
        # Associate with property if exists
        if property_id:
            try:
                property_obj = Property.objects.get(id=property_id)
                lead.interested_property = property_obj
                lead.save()
                
                # Increment property inquiries count
                property_obj.inquiries_count += 1
                property_obj.save(update_fields=['inquiries_count'])
            except Property.DoesNotExist:
                pass
        
        # Send email notification to admin
        try:
            subject = f"New Lead: {lead.full_name}"
            message_body = f"""
            New lead received via {lead.get_source_display()}.
            
            Name: {lead.full_name}
            Email: {lead.email}
            Phone: {lead.phone}
            Property: {lead.interested_property.title if lead.interested_property else 'General Enquiry'}
            Message: {lead.message}
            
            View in Admin: {request.build_absolute_uri(reverse('admin:leads_lead_change', args=[lead.id]))}
            """
            
            # Send to configured ADMINS or fallback to info email
            recipient_list = [email for _, email in getattr(settings, 'ADMINS', [])] or ['info@kalpvriksh.com']
            
            send_mail(subject, message_body, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
        except Exception as e:
            print(f"Error sending lead notification: {e}")
        
        # Success message
        messages.success(request, 'Thank you for your interest! Our team will contact you shortly.')
        
        # Redirect to thank you page
        return redirect('thank_you')
    
    return redirect('home')

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name', '')
        
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            
            if created:
                messages.success(request, 'Successfully subscribed to newsletter!')
            else:
                messages.info(request, 'You are already subscribed to our newsletter.')
        else:
            messages.error(request, 'Please provide a valid email address.')
        
        return redirect('thank_you')
    
    return redirect('home')

def careers(request):
    # Fetch active job positions from the database
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'jobs': jobs
    }
    return render(request, 'careers.html', context)

def thank_you(request):
    return render(request, 'leads/thank_you.html')

def chatbot_api(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            message = data.get('message', '').lower()
            
            # --- Chatbot Training: Greetings ---
            greetings = ['hi', 'hello', 'hey', 'greetings', 'good morning', 'good evening']
            if any(word in message for word in greetings):
                return JsonResponse({
                    'response': 'Hello! Welcome to Kalpvriksh Real Estate. How can I assist you in finding your dream home today?',
                    'properties': [],
                    'logo_url': getattr(settings, 'SITE_LOGO_URL', '')
                })

            # --- Chatbot Training: Amenities ---
            amenity_keywords = ['pool', 'gym', 'garden', 'clubhouse', 'parking']
            amenity_filter = Q()
            for amenity in amenity_keywords:
                if amenity in message:
                    # Assuming description contains amenity info
                    amenity_filter |= Q(description__icontains=amenity)

            # Initialize filters
            filters = Q()
            
            # 1. Extract BHK/Bedrooms
            if '1 bhk' in message or '1 bed' in message: filters &= Q(bedrooms=1)
            elif '2 bhk' in message or '2 bed' in message: filters &= Q(bedrooms=2)
            elif '3 bhk' in message or '3 bed' in message: filters &= Q(bedrooms=3)
            elif '4 bhk' in message or '4 bed' in message: filters &= Q(bedrooms=4)
            elif '5 bhk' in message or '5 bed' in message: filters &= Q(bedrooms=5)
            
            # 2. Extract Location Keywords
            # Filter out common words to find potential location names
            stop_words = ['i', 'want', 'need', 'looking', 'for', 'a', 'in', 'at', 'near', 'property', 'flat', 'apartment', 'villa', 'home', 'house', 'bhk', 'budget', 'price', 'buy', 'hi', 'hello']
            potential_keywords = [w for w in message.split() if w not in stop_words and len(w) > 2]
            
            location_query = Q()
            for word in potential_keywords:
                # Check if word matches city, sublocation, or title
                location_query |= Q(sublocation__name__icontains=word) | Q(city__name__icontains=word) | Q(title__icontains=word)
            
            if location_query:
                filters &= location_query
            
            if amenity_filter:
                filters &= amenity_filter

            # 3. Query Database
            properties = Property.objects.filter(filters).distinct()[:3]
            
            response_data = {
                'response': '',
                'properties': [],
                'logo_url': getattr(settings, 'SITE_LOGO_URL', '')
            }
            
            if properties.exists():
                response_data['response'] = f"I found {properties.count()} properties that match your criteria:"
                for p in properties:
                    # Use provided Pune image as fallback if property has no image
                    image_url = ''
                    if p.main_image:
                        image_url = p.main_image.url
                    elif p.city and p.city.image:
                        image_url = p.city.image.url
                    elif p.city and p.city.name.lower() == 'pune':
                        image_url = 'https://www.birlaadvaya.org.in/images/birla/pune-maharashtra.webp'

                    response_data['properties'].append({
                        'title': p.title,
                        'price': p.price, # We will format this in JS
                        'location': f"{p.sublocation.name}, {p.city.name}",
                        'image': image_url,
                        'rera': p.rera_number,
                        'url': p.get_absolute_url()
                    })
            else:
                response_data['response'] = "I couldn't find exact matches. Try specifying a location like 'Baner' or configuration like '3 BHK'."
            
            # --- Chatbot Training: Lead Capture & WhatsApp Redirect ---
            requirement_keywords = ['bhk', 'budget', 'looking', 'buy', 'flat', 'apartment', 'villa']
            if any(k in message for k in requirement_keywords):
                # Store the conversation as a Lead
                Lead.objects.create(
                    first_name="Chatbot",
                    last_name="Lead",
                    message=f"Requirement captured via chatbot: {message}",
                    source='chatbot'
                )
                response_data['response'] += "\n\nI've noted your requirements. I'm redirecting you to our WhatsApp expert for immediate assistance..."
                response_data['redirect_url'] = f"https://wa.me/919270096195?text=Hello,%20I'm%20interested%20in%20properties.%20My%20requirement:%20{message}"
                
            return JsonResponse(response_data)
        except Exception as e:
            # Return a polite error message in JSON format so the frontend doesn't break
            return JsonResponse({'response': "I'm sorry, I encountered a slight hiccup while searching. Could you please try asking in a different way?", 'properties': []})
            
    return JsonResponse({'error': 'Invalid request'}, status=400)
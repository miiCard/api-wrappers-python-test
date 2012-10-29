# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from TestHarness.models import HarnessViewModel
from django.utils.html import escape

from MiiCardConsumers import MiiCardOAuthClaimsService, MiiCardServiceUrls

def home(request):
    view_model = HarnessViewModel()

    action = None

    if request.method == "POST":
        # Try parsing the form params (if any)
        view_model.consumer_key = request.POST['oauth-consumer-key']
        view_model.consumer_secret = request.POST['oauth-consumer-secret']
        view_model.access_token = request.POST['oauth-access-token']
        view_model.access_token_secret = request.POST['oauth-access-token-secret']

        view_model.social_account_type = request.POST['social-account-type']
        view_model.social_account_id = request.POST['social-account-id']

        view_model.assurance_image_type = request.POST['assurance-image-type']

        action = request.POST['btn-invoke']

    if action and view_model.consumer_key and view_model.consumer_secret and view_model.access_token and view_model.access_token_secret:
        api = MiiCardOAuthClaimsService(view_model.consumer_key, view_model.consumer_secret, view_model.access_token, view_model.access_token_secret)
        
        if action == "get-claims":
            view_model.last_get_claims_result = prettify_response(api.get_claims(), prettify_claims)
        elif action == 'is-user-assured':
            view_model.last_is_user_assured_result = prettify_response(api.is_user_assured(), None)
        elif action == 'is-social-account-assured' and view_model.social_account_type and view_model.social_account_id:
            view_model.last_is_social_account_assured_result = prettify_response(api.is_social_account_assured(view_model.social_account_id, view_model.social_account_type), None);
        elif action == 'assurance-image' and view_model.assurance_image_type:
            view_model.show_assurance_image = True
    elif action:
        view_model.show_oauth_details_required_error = True

    return render_to_response('index.html', { 'view_model': view_model }, context_instance=RequestContext(request))

def assuranceimage(request):
    consumer_key = request.GET['oauth-consumer-key']
    consumer_secret = request.GET['oauth-consumer-secret']
    access_token = request.GET['oauth-access-token']
    access_token_secret = request.GET['oauth-access-token-secret']
    type = request.GET['type']

    if consumer_key and consumer_secret and access_token and access_token_secret and type:
        api = MiiCardOAuthClaimsService(consumer_key, consumer_secret, access_token, access_token_secret)
        response = api.assurance_image(type)
    
        toReturn = HttpResponse(response, mimetype='image/png')
        toReturn['Content-Length'] = len(response)

        return toReturn

def prettify_response(response, data_processor):
    toReturn = '<div class="response">'
    toReturn += render_fact('Status', response.status)
    toReturn += render_fact('Error code', response.error_code)
    toReturn += render_fact('Error message', response.error_message)
    
    if not data_processor:
        toReturn += render_fact('Data', response.data.__str__())

    toReturn += '</div>'
    
    if data_processor:
        toReturn += data_processor(response.data)

    return toReturn

def prettify_claims(claims_obj):
    toReturn = '<div class="fact">'
    toReturn += "<h2>User profile</h2>"

    # Dump top-level properties
    toReturn += render_fact('Username', claims_obj.username)
    toReturn += render_fact('Salutation', claims_obj.salutation)
    toReturn += render_fact('First name', claims_obj.first_name)
    toReturn += render_fact('Middle name', claims_obj.middle_name)
    toReturn += render_fact('Last name', claims_obj.last_name)
    toReturn += render_fact('Identity verified?', claims_obj.identity_assured)
    toReturn += render_fact('Identity last verified', claims_obj.last_verified)
    toReturn += render_fact('Has a public profile?', claims_obj.has_public_profile)
    toReturn += render_fact('Previous first name', claims_obj.previous_first_name)
    toReturn += render_fact('Previous middle name', claims_obj.previous_middle_name)
    toReturn += render_fact('Previous last name', claims_obj.previous_last_name)
    toReturn += render_fact('Profile URL', claims_obj.profile_url)
    toReturn += render_fact('Profile short URL', claims_obj.profile_short_url)
    toReturn += render_fact('Card image URL', claims_obj.card_image_url)

    toReturn += render_fact_heading('Postal addresses')
    ct = 0
    for address in claims_obj.postal_addresses or []:
        toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
        toReturn += render_address(address)
        toReturn += '</div>'
        ct += 1

    toReturn += render_fact_heading('Phone numbers')
    ct = 0
    for phone in claims_obj.phone_numbers or []:
        toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
        toReturn += render_phone_number(phone)
        toReturn += '</div>'
        ct += 1

    toReturn += render_fact_heading('Email addresses') 
    ct = 0
    for email in claims_obj.email_addresses or []:
        toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
        toReturn += render_email(email)
        toReturn += '</div>'
        ct += 1

    toReturn += render_fact_heading('Internet identities')
    ct = 0
    for identity in claims_obj.identities or []:
        toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
        toReturn += render_identity(identity)
        toReturn += '</div>'
        ct += 1

    toReturn += render_fact_heading('Web properties')
    ct = 0
    for web in claims_obj.web_properties or []:
        toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
        toReturn += render_web_property(web)
        toReturn += '</div>'
        ct += 1

    if claims_obj.public_profile:
        toReturn += '<div class="fact"><h4>Public profile data</h4>'
        toReturn += prettify_claims(claims_obj.public_profile)
        toReturn += '</div>'

    toReturn += '</div>'

    return toReturn
   
def render_fact_heading(heading):
    return "<h3>" + heading + "</h3>"

def render_fact(fact_name, fact_value):
    return '<div class="fact-row"><span class="fact-name">' + fact_name + '</span><span class="fact-value">' + (escape(fact_value.__str__() or '[Empty]')) + "</span></div>"

def render_phone_number(phone_number):
    toReturn = '<div class="fact">'

    toReturn += render_fact('Display name', phone_number.display_name)
    toReturn += render_fact('Country code', phone_number.country_code)
    toReturn += render_fact('National number', phone_number.national_number)
    toReturn += render_fact('Is mobile?', phone_number.is_mobile)
    toReturn += render_fact('Is primary?', phone_number.is_primary)
    toReturn += render_fact('Verified?', phone_number.verified)

    toReturn += '</div>'

    return toReturn

def render_address(address):
    toReturn = '<div class="fact">'

    toReturn += render_fact('House', address.house)
    toReturn += render_fact('Line1', address.line1)
    toReturn += render_fact('Line2', address.line2)
    toReturn += render_fact('City', address.city)
    toReturn += render_fact('Region', address.region)
    toReturn += render_fact('Code', address.code)
    toReturn += render_fact('Country', address.country)
    toReturn += render_fact('Is primary?', address.is_primary)
    toReturn += render_fact('Verified?', address.verified)

    toReturn += '</div>'

    return toReturn

def render_email(email):
    toReturn = '<div class="fact">'

    toReturn += render_fact('Display name', email.display_name)
    toReturn += render_fact('Address', email.address)
    toReturn += render_fact('Is primary?', email.is_primary)
    toReturn += render_fact('Verified?', email.verified)

    toReturn += '</div>'

    return toReturn

def render_web_property(property):
    toReturn = '<div class="fact">'

    toReturn += render_fact('Display name', property.display_name)
    toReturn += render_fact('Identifier', property.identifier)
    toReturn += render_fact('Type', property.type)
    toReturn += render_fact('Verified?', property.verified)

    toReturn += '</div>'

    return toReturn

def render_identity(identity):
    toReturn = '<div class="fact">'

    toReturn += render_fact('Source', identity.source)
    toReturn += render_fact('User ID', identity.user_id)
    toReturn += render_fact('Profile URL', identity.profile_url)
    toReturn += render_fact('Verified?', identity.verified)

    toReturn += '</div>'

    return toReturn
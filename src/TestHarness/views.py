# Create your views here.
from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.context_processors import csrf
from TestHarness.models import HarnessViewModel
from django.utils.html import escape

from MiiCardConsumers import MiiCardOAuthClaimsService, MiiCardOAuthFinancialService, MiiCardDirectoryService, MiiCardServiceUrls

def home(request):
    view_model = HarnessViewModel()

    action = None

    if request.method == "POST":
        # Try parsing the form params (if any)
        view_model.consumer_key = request.POST.get('oauth-consumer-key', None)
        view_model.consumer_secret = request.POST.get('oauth-consumer-secret', None)
        view_model.access_token = request.POST.get('oauth-access-token', None)
        view_model.access_token_secret = request.POST.get('oauth-access-token-secret', None)

        view_model.social_account_type = request.POST.get('social-account-type', None)
        view_model.social_account_id = request.POST.get('social-account-id', None)

        view_model.assurance_image_type = request.POST.get('assurance-image-type', None)

        view_model.snapshot_id = request.POST.get('snapshot-id', None)
        view_model.snapshot_details_id = request.POST.get('snapshot-details-id', None)
        view_model.snapshot_pdf_id = request.POST.get('snapshot-pdf-id', None)
        view_model.snapshot_authentication_details_id = request.POST.get('snapshot-authentication-details-id', None)

        view_model.card_image_format = request.POST.get('card-image-format', None)
        view_model.card_image_show_email_address = request.POST.get('card-image-show-email-address', 'off') == 'on'
        view_model.card_image_show_phone_number = request.POST.get('card-image-show-phone-number', 'off') == 'on'
        view_model.card_image_snapshot_id = request.POST.get('card-image-snapshot-id', None)

        view_model.financial_data_modesty_limit = request.POST.get('financial-data-modesty-limit', None)
        view_model.financial_data_credit_cards_modesty_limit = request.POST.get('financial-data-credit-cards-modesty-limit', None)

        view_model.directory_criterion = request.POST.get('directory_criterion', '')
        view_model.directory_criterion_value = request.POST.get('directory_criterion_value', '')
        view_model.directory_criterion_value_hashed = request.POST.get('directory_criterion_value_hashed', 'off') == 'on'

        action = request.POST.get('btn-invoke', None)

    if action and action == "directory-search":
        directory_result = MiiCardDirectoryService().find_by(view_model.directory_criterion, view_model.directory_criterion_value, view_model.directory_criterion_value_hashed)
        if directory_result is not None:
            view_model.last_directory_search_result = prettify_claims(directory_result)
    elif action and view_model.consumer_key and view_model.consumer_secret and view_model.access_token and view_model.access_token_secret:
        api = MiiCardOAuthClaimsService(view_model.consumer_key, view_model.consumer_secret, view_model.access_token, view_model.access_token_secret)
        financial_api = MiiCardOAuthFinancialService(view_model.consumer_key, view_model.consumer_secret, view_model.access_token, view_model.access_token_secret)
        
        if action == "get-claims":
            view_model.last_get_claims_result = prettify_response(api.get_claims(), prettify_claims)
        elif action == 'is-user-assured':
            view_model.last_is_user_assured_result = prettify_response(api.is_user_assured(), None)
        elif action == 'is-social-account-assured' and view_model.social_account_type and view_model.social_account_id:
            view_model.last_is_social_account_assured_result = prettify_response(api.is_social_account_assured(view_model.social_account_id, view_model.social_account_type), None)
        elif action == 'assurance-image' and view_model.assurance_image_type:
            view_model.show_assurance_image = True
        elif action == 'card-image':
            view_model.show_card_image = True
        elif action == 'get-identity-snapshot-details':
            view_model.last_get_identity_snapshot_details_result = prettify_response(api.get_identity_snapshot_details(view_model.snapshot_details_id), prettify_identity_snapshot_details)
        elif action == 'get-identity-snapshot' and view_model.snapshot_id:
            view_model.last_get_identity_snapshot_result = prettify_response(api.get_identity_snapshot(view_model.snapshot_id), prettify_identity_snapshot)
        elif action == 'get-authentication-details':
            view_model.last_get_authentication_details_result = prettify_response(api.get_authentication_details(view_model.snapshot_authentication_details_id), prettify_identity_snapshot_authentication_details)
        elif action == 'get-identity-snapshot-pdf' and view_model.snapshot_pdf_id:
            response = api.get_identity_snapshot_pdf(view_model.snapshot_pdf_id)

            toReturn = HttpResponse(response, mimetype='application/pdf')
            toReturn['Content-Length'] = len(response)
            toReturn['Content-Disposition'] = 'attachment; filename="' + view_model.snapshot_pdf_id + '"'

            return toReturn
        elif action == 'is-refresh-in-progress':
            view_model.is_refresh_in_progress_result = prettify_response(financial_api.is_refresh_in_progress(), None)
        elif action == 'is-refresh-in-progress-credit-cards':
            view_model.is_refresh_in_progress_credit_cards_result = prettify_response(financial_api.is_refresh_in_progress_credit_cards(), None)
        elif action == 'refresh-financial-data':
            view_model.refresh_financial_data_result = prettify_response(financial_api.refresh_financial_data(), prettify_refresh_financial_data)
        elif action == 'refresh-financial-data-credit-cards':
            view_model.refresh_financial_data_credit_cards_result = prettify_response(financial_api.refresh_financial_data(), prettify_refresh_financial_data_credit_cards)
        elif action == 'get-financial-transactions':
            configuration = PrettifyConfiguration(view_model.financial_data_modesty_limit)
            view_model.get_financial_transactions_result = prettify_response(financial_api.get_financial_transactions(), prettify_financial_transactions, configuration)
        elif action == 'get-financial-transactions-credit-cards':
            configuration = PrettifyConfiguration(view_model.financial_data_credit_cards_modesty_limit)
            view_model.get_financial_transactions_credit_cards_result = prettify_response(financial_api.get_financial_transactions_credit_cards(), prettify_financial_transactions, configuration)

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

def cardimage(request):
    consumer_key = request.GET['oauth-consumer-key']
    consumer_secret = request.GET['oauth-consumer-secret']
    access_token = request.GET['oauth-access-token']
    access_token_secret = request.GET['oauth-access-token-secret']

    format = request.GET['format']
    snapshot_id = request.GET['snapshot-id']
    show_email_address = request.GET['show-email-address'] == "True"
    show_phone_number = request.GET['show-phone-number'] == "True"

    if consumer_key and consumer_secret and access_token and access_token_secret:
        api = MiiCardOAuthClaimsService(consumer_key, consumer_secret, access_token, access_token_secret)
        response = api.get_card_image(snapshot_id, show_email_address, show_phone_number, format)

        toReturn = HttpResponse(response, mimetype='image/png')
        toReturn['Content-Length'] = len(response)
        
        return toReturn

def sha1(request):
    identifier = request.GET['identifier']
    response = MiiCardDirectoryService().hash_identifier(identifier)

    toReturn = HttpResponse(response, mimetype='text/plain')
    toReturn['Content-Length'] = len(response)

    return toReturn

def prettify_response(response, data_processor, configuration = None):
    toReturn = '<div class="response">'
    toReturn += render_fact('Status', response.status)
    toReturn += render_fact('Error code', response.error_code)
    toReturn += render_fact('Error message', response.error_message)
    toReturn += render_fact('Is a test user?', response.is_test_user)
    
    if response.data is not None:
        if not data_processor:
            toReturn += render_fact('Data', response.data.__str__())

        toReturn += '</div>'
    
        if data_processor:
            if type(response.data) is list:
                ct = 0

                for data_item in response.data:
                    toReturn += "<div class='fact'><h4>[" + ct.__str__() + "]</h4>";
                    toReturn += data_processor(data_item, configuration)
                    toReturn += "</div>"

                    ct += 1
            else:
                toReturn += data_processor(response.data, configuration)
    else:
        toReturn += render_fact('Data', None)

    return toReturn

def prettify_identity_snapshot_details(snapshot_details, configuration = None):
    toReturn = "<div class='fact'>"

    toReturn += render_fact("Snapshot ID", snapshot_details.snapshot_id)
    toReturn += render_fact("Username", snapshot_details.username)
    toReturn += render_fact("Timestamp",  snapshot_details.timestamp_utc)
    toReturn += render_fact("Was a test user?", snapshot_details.was_test_user)
    toReturn += "</div>"

    return toReturn

def prettify_identity_snapshot(identity_snapshot, configuration = None):
    toReturn = "<div class='fact'>"

    toReturn += render_fact_heading("Snapshot details")
    toReturn += prettify_identity_snapshot_details(identity_snapshot.details, configuration)

    toReturn += render_fact_heading("Snapshot contents")
    toReturn += prettify_claims(identity_snapshot.snapshot, configuration)

    toReturn += "</div>"

    return toReturn

def prettify_identity_snapshot_authentication_details(snapshot_authenitcation_details, configuration = None):
    toReturn = "<div class='fact'>"
    toReturn += "<h2>Authentication Details</h2>"

    toReturn += render_fact('Authentication time (UTC)', snapshot_authenitcation_details.authentication_time_utc)
    toReturn += render_fact('Second factor token type', snapshot_authenitcation_details.second_factor_token_type)
    toReturn += render_fact('Second factor provider', snapshot_authenitcation_details.second_factor_provider)

    toReturn += render_fact_heading('Locations')
    ct = 0
    for location in snapshot_authenitcation_details.locations or []:
        toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
        toReturn += render_location(location)
        toReturn += '</div>'
        ct += 1

    toReturn += "</div>"

    return toReturn

def prettify_claims(claims_obj, configuration = None):
    toReturn = '<div class="fact">'
    toReturn += "<h2>User profile</h2>"

    # Dump top-level properties
    toReturn += render_fact('Username', claims_obj.username)
    toReturn += render_fact('Salutation', claims_obj.salutation)
    toReturn += render_fact('First name', claims_obj.first_name)
    toReturn += render_fact('Middle name', claims_obj.middle_name)
    toReturn += render_fact('Last name', claims_obj.last_name)
    toReturn += render_fact('Date of birth', claims_obj.date_of_birth)
    toReturn += render_fact('Age', claims_obj.age)
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
        toReturn += prettify_claims(claims_obj.public_profile, configuration)
        toReturn += '</div>'

    toReturn += '</div>'

    return toReturn
   
def prettify_refresh_financial_data(financial_refresh_status, configuration = None):
    toReturn = "<div class='fact'>"
    toReturn += "<h2>Financial Refresh Status</h2>"

    toReturn += render_fact('State', financial_refresh_status.state)

    toReturn += "</div>"

    return toReturn

def prettify_financial_transactions(financial_transactions, configuration = None):
    toReturn = "<div class='fact'>"
    toReturn += "<h2>Financial Data</h2>"
    toReturn += render_fact_heading('Financial Providers')

    ct = 0
    for financial_provider in financial_transactions.financial_providers or []:
        toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
        toReturn += render_financial_provider(financial_provider, configuration)
        toReturn += '</div>'
        ct += 1

    toReturn += "</div>"

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

def render_location(location):
    toReturn = '<div class="fact">'

    toReturn += render_fact('Provider', location.location_provider)
    toReturn += render_fact('Latitude', location.latitude)
    toReturn += render_fact('Longitude', location.longitude)
    toReturn += render_fact('Accuracy (metres)', location.lat_long_accuracy_metres)

    toReturn += render_address(location.approximate_address)

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

def render_financial_provider(financial_provider, configuration = None):
    toReturn = '<div class="fact">'
    toReturn += render_fact('Name', financial_provider.provider_name)

    ct = 0
    if financial_provider.financial_accounts:
        toReturn += render_fact_heading('Financial Accounts')

        for financial_account in financial_provider.financial_accounts:
            toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
            toReturn += render_financial_account(financial_account, configuration)
            toReturn += '</div>'
            ct += 1
    elif financial_provider.financial_credit_cards:
        toReturn += render_fact_heading('Financial Credit Cards')

        for financial_credit_card in financial_provider.financial_credit_cards:
            toReturn += '<div class="fact"><h4>[' + ct.__str__() + ']</h4>'
            toReturn += render_financial_credit_card(financial_credit_card, configuration)
            toReturn += '</div>'
            ct += 1

    toReturn += '</div>';

    return toReturn

def render_financial_account(financial_account, configuration = None):
    toReturn = '<div class="fact">'

    toReturn += render_fact('Holder', financial_account.holder)
    toReturn += render_fact('Account Name', financial_account.account_name)
    toReturn += render_fact('Sort Code', financial_account.sort_code)
    toReturn += render_fact('Account Number', financial_account.account_number)
    toReturn += render_fact('Type', financial_account.type)
    toReturn += render_fact('Last Updated (UTC)', financial_account.last_updated_utc)
    toReturn += render_fact('From Date', financial_account.from_date)
    toReturn += render_fact('Currency ISO', financial_account.currency_iso)
    toReturn += render_fact('Closing Balance', get_modesty_filtered_amount(financial_account.closing_balance, configuration))
    toReturn += render_fact('Credits Count', financial_account.credits_count)
    toReturn += render_fact('Credits Sum', get_modesty_filtered_amount(financial_account.credits_sum, configuration))
    toReturn += render_fact('Debits Count', financial_account.debits_count)
    toReturn += render_fact('Debits Sum', get_modesty_filtered_amount(financial_account.debits_sum, configuration))

    toReturn += render_fact_heading('Transactions')

    toReturn += "<table class='table table-striped table-condensed table-hover'><thead><tr><th>Date</th><th>Description</th><th class='r'>Credit</th><th class='r'>Debit</th></tr></thead><tbody>"

    for transaction in financial_account.transactions or []:
        toReturn += "<tr><td>" + transaction.date.__str__() + "</td><td title='ID: " + transaction.id + "'>" + transaction.description + "</td><td class='r'>" + get_modesty_filtered_amount(transaction.amount_credited, configuration) + "</td><td class='r d'>" + get_modesty_filtered_amount(transaction.amount_debited, configuration) + "</td></tr>"

    toReturn += "</tbody></table>"

    toReturn += '</div>';

    return toReturn

def render_financial_credit_card(financial_credit_card, configuration = None):
    toReturn = '<div class="fact">'

    toReturn += render_fact('Holder', financial_credit_card.holder)
    toReturn += render_fact('Account Name', financial_credit_card.account_name)
    toReturn += render_fact('Account Number', financial_credit_card.account_number)
    toReturn += render_fact('Type', financial_credit_card.type)
    toReturn += render_fact('Last Updated (UTC)', financial_credit_card.last_updated_utc)
    toReturn += render_fact('From Date', financial_credit_card.from_date)
    toReturn += render_fact('Currency ISO', financial_credit_card.currency_iso)
    toReturn += render_fact('Credit Limit', get_modesty_filtered_amount(financial_credit_card.credit_limit, configuration))
    toReturn += render_fact('Running Balance', get_modesty_filtered_amount(financial_credit_card.running_balance, configuration))
    toReturn += render_fact('Credits Count', financial_credit_card.credits_count)
    toReturn += render_fact('Credits Sum', get_modesty_filtered_amount(financial_credit_card.credits_sum, configuration))
    toReturn += render_fact('Debits Count', financial_credit_card.debits_count)
    toReturn += render_fact('Debits Sum', get_modesty_filtered_amount(financial_credit_card.debits_sum, configuration))

    toReturn += render_fact_heading('Transactions')

    toReturn += "<table class='table table-striped table-condensed table-hover'><thead><tr><th>Date</th><th>Description</th><th class='r'>Credit</th><th class='r'>Debit</th></tr></thead><tbody>"

    for transaction in financial_credit_card.transactions or []:
        toReturn += "<tr><td>" + transaction.date.__str__() + "</td><td title='ID: " + transaction.id + "'>" + transaction.description + "</td><td class='r'>" + get_modesty_filtered_amount(transaction.amount_credited, configuration) + "</td><td class='r d'>" + get_modesty_filtered_amount(transaction.amount_debited, configuration) + "</td></tr>"

    toReturn += "</tbody></table>"

    toReturn += '</div>';

    return toReturn

def get_modesty_filtered_amount(amount, configuration):
    toReturn = ''

    if amount is not None:
        limit = None

        if configuration is not None and configuration.get_modesty_limit() is not None:
            limit = configuration.get_modesty_limit()

        if limit is None or amount <= limit:
            toReturn = format(amount, "0.2f")
        else:
            toReturn = '?.??'

    return toReturn

class PrettifyConfiguration:
    def __init__(
                 self,
                 modesty_limit
                 ):

        if modesty_limit:
            self.modesty_limit = int(modesty_limit)
        else:
            self.modesty_limit = None

    def get_modesty_limit(self):
        return self.modesty_limit
from django.db import models

# Create your models here.
class OAuthDetails(models.Model):
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''

class HarnessViewModel(models.Model):
    oauth_details = ''

    last_get_claims_result = ''
    last_is_user_assured_result = ''
    last_is_social_account_assured_result = ''
    last_get_identity_snapshot_details_result = ''
    last_get_identity_snapshot_result = ''
    last_get_authentication_details_result = ''
    show_assurance_image = ''

    assurance_image_type = ''

    social_account_id = ''
    social_account_type = ''

    snapshot_details_id = ''
    snapshot_id = ''
    snapshot_pdf_id = ''
    snapshot_authentication_details_id = ''

    card_image_snapshot_id = ''
    card_image_show_email_address = False
    card_image_show_phone_number = False
    card_image_format = ''
    show_card_image = False

    show_oauth_details_required_error = False

    is_refresh_in_progress_result = ''
    refresh_financial_data_result = ''
    get_financial_transactions_result = ''
    financial_data_modesty_limit = 100

    directory_criterion = ''
    directory_criterion_value = ''
    directory_criterion_value_hashed = False
    last_directory_search_result = ''
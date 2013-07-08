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
    show_assurance_image = ''

    assurance_image_type = ''

    social_account_id = ''
    social_account_type = ''

    snapshot_details_id = ''
    snapshot_id = ''
    snapshot_pdf_id = ''

    show_oauth_details_required_error = False
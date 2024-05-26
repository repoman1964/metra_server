import phonenumbers
from phonenumbers import geocoder, carrier, timezone

def format_phone_number(phone_number, region='US'):
    try:
        # Parse the phone number
        parsed_number = phonenumbers.parse(phone_number, region)
        
        # Check if the number is valid
        if not phonenumbers.is_valid_number(parsed_number):
            return "Invalid phone number"
        
        # Get the international format
        international_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        # Get the national format
        national_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
        
        # Get the E164 format
        e164_format = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
        # Get the possible regions
        possible_regions = phonenumbers.region_code_for_number(parsed_number)
        
        # Get the carrier name
        carrier_name = carrier.name_for_number(parsed_number, 'en')
        
        # Get the timezone
        time_zones = timezone.time_zones_for_number(parsed_number)
        
        # Get the description for the number
        description = geocoder.description_for_number(parsed_number, 'en')
        
        return {
            "international_format": international_format,
            "national_format": national_format,
            "e164_format": e164_format,
            "possible_regions": possible_regions,
            "carrier_name": carrier_name,
            "time_zones": time_zones,
            "description": description
        }
    except phonenumbers.NumberParseException as e:
        return str(e)

# Example usage
phone_number = "+14155552671"
formatted_number = format_phone_number(phone_number)
print(formatted_number)

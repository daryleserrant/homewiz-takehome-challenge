import re
from dateutil import parser
from datetime import datetime
from backend.db import check_inventory, insert_user, find_existing_user, get_next_available_slot, insert_booking, get_property_by_id
from backend.utils import send_confirmation_email

def validate_email(email: str) -> bool:
     '''
     Validate email address. Returns True if the email address is valid, false otherwise.
     '''
     email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
     if not re.match(email_regex, email):
       return False
     return True

def validate_phone(phone: str) -> bool:
    '''
    Validate phone number. Returns True if the phone number is valid, false otherwise.
    '''
    phone_regex = r"^(?:\+1\s?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$"
    if not re.match(phone_regex, phone):
      return False
    return True

def validate_move_in_date(date: str) -> bool:
    '''
    Validate move-in date. Returns False if date is earlier than today's date or invalid format.
    '''
    try:
      datetime_object = parser.parse(date)
    except parser.ParserError:
      return False
    if datetime_object < datetime.now():
      return False
    return True

def validate_beds(beds: str) -> bool:
    '''
    Validate number of bedrooms. Returns True if numeric value is provided that is greater than 0, false otherwise.
    '''
    if beds.isnumeric():
      if int(beds) > 0:
        return True
      else:
        return False
    return False

def store_prospect_info(name: str, email: str, phone: str) -> int:
  '''
  Store prospect information in a database. Return the ID of the stored information.
  '''
  # Check if the email already exists
  existing_user_id = find_existing_user(email)
  if existing_user_id:
    return existing_user_id
  # If not, insert a new user
  return insert_user(name, email, phone)
  
def check_availability(beds: int) -> int:
    """
    Check inventory for available properties based on the number of beds.
    """
    return check_inventory(beds)

def book_tour(unit:int, user_name: str, user_email: str, user_id: int) -> str:
    """
    Book a tour for the prospect and send a confirmation email."""

    # Find the next available time slot for the selected property
    slot = get_next_available_slot(unit)
    if not slot:
        return "No available slots for this property"
  
    # Insert a new booking record
    booking_id = insert_booking(user_id, unit, slot["id"])

    # Retrieve property information
    property_info = get_property_by_id(unit)
    if not property_info:
        return "Property not found."
    
    # Send confirmation email
    send_confirmation_email(
        name=user_name,
        email=user_email,
        property=property_info,
        start_time=slot["start_time"]
    )
    return "Confirmation email sent"
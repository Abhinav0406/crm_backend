#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.support.models import SupportTicket, TicketMessage
from apps.support.serializers import TicketMessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def test_support_api():
    print("Testing Support API...")
    
    # Test 1: Check if models exist
    print(f"1. SupportTicket count: {SupportTicket.objects.count()}")
    print(f"2. TicketMessage count: {TicketMessage.objects.count()}")
    
    # Test 2: Check if we have a ticket
    ticket = SupportTicket.objects.first()
    if ticket:
        print(f"3. First ticket: {ticket.ticket_id} (ID: {ticket.id})")
        print(f"4. Ticket messages: {ticket.messages.count()}")
        
        # Test 3: Check if we have messages
        message = TicketMessage.objects.first()
        if message:
            print(f"5. First message: {message}")
            print(f"6. Message sender: {message.sender}")
            print(f"7. Message sender role: {message.sender.role}")
            print(f"8. Message sender tenant: {message.sender.tenant}")
            
            # Test 4: Test serializer
            try:
                serializer = TicketMessageSerializer(message)
                data = serializer.data
                print(f"9. Serializer data keys: {list(data.keys())}")
                print(f"10. Serializer success: {data.get('id') == message.id}")
            except Exception as e:
                print(f"9. Serializer error: {e}")
    
    # Test 5: Test filtering by ticket ID
    if ticket:
        messages = TicketMessage.objects.filter(ticket_id=ticket.id)
        print(f"11. Messages filtered by ticket ID {ticket.id}: {messages.count()}")
        
        messages = TicketMessage.objects.filter(ticket__ticket_id=ticket.ticket_id)
        print(f"12. Messages filtered by ticket_id {ticket.ticket_id}: {messages.count()}")

if __name__ == "__main__":
    test_support_api() 
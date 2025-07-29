   from apps.clients.models import AuditLog, Client

   # Replace with the actual client ID you want to check
   client_id = 15  # Change this to your customer's ID

   logs = AuditLog.objects.filter(client_id=client_id).order_by('-timestamp')
   for log in logs:
       print(f"Action: {log.action}, User: {log.user}, Time: {log.timestamp}")
       print(f"Before: {log.before}")
       print(f"After: {log.after}")
       print("-" * 40)

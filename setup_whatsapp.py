#!/usr/bin/env python3
"""
WhatsApp Business API Setup Script
This script helps you configure WhatsApp Business API integration for your CRM.
"""

import os
import sys
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WhatsAppSetup:
    def __init__(self):
        self.config_file = Path('.env')
        self.example_file = Path('env.example')
        
    def print_header(self):
        print("=" * 60)
        print("WhatsApp Business API Setup for CRM")
        print("=" * 60)
        print()
        
    def print_step(self, step_num, title):
        print(f"Step {step_num}: {title}")
        print("-" * 40)
        
    def check_prerequisites(self):
        """Check if required files exist"""
        self.print_step(1, "Checking Prerequisites")
        
        if not self.example_file.exists():
            print("❌ env.example file not found!")
            return False
            
        if not self.config_file.exists():
            print("⚠️  .env file not found. Will create one from env.example")
            self.create_env_file()
            
        print("✅ Prerequisites check completed")
        return True
        
    def create_env_file(self):
        """Create .env file from env.example if it doesn't exist"""
        if self.example_file.exists():
            with open(self.example_file, 'r') as f:
                content = f.read()
            
            with open(self.config_file, 'w') as f:
                f.write(content)
            print("✅ Created .env file from env.example")
            
    def get_user_input(self, prompt, default=""):
        """Get user input with optional default value"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
            
    def configure_whatsapp_credentials(self):
        """Configure WhatsApp API credentials"""
        self.print_step(2, "Configure WhatsApp API Credentials")
        
        print("Please enter your WhatsApp Business API credentials from Meta Developer Console:")
        print()
        
        # Phone Number ID
        phone_number_id = self.get_user_input(
            "Enter your Phone Number ID (from Meta Developer Console)",
            os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
        )
        
        # Access Token
        access_token = self.get_user_input(
            "Enter your Access Token (from Meta Developer Console)",
            os.getenv('WHATSAPP_ACCESS_TOKEN', '')
        )
        
        # Verify Token
        verify_token = self.get_user_input(
            "Enter your custom Verify Token (create a strong, unique string)",
            os.getenv('WHATSAPP_VERIFY_TOKEN', 'your-crm-whatsapp-verify-2024')
        )
        
        # Business Account ID (optional)
        business_account_id = self.get_user_input(
            "Enter your Business Account ID (optional)",
            os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
        )
        
        # App ID (optional)
        app_id = self.get_user_input(
            "Enter your App ID (optional)",
            os.getenv('WHATSAPP_APP_ID', '')
        )
        
        # Update .env file
        self.update_env_file({
            'WHATSAPP_PHONE_NUMBER_ID': phone_number_id,
            'WHATSAPP_ACCESS_TOKEN': access_token,
            'WHATSAPP_VERIFY_TOKEN': verify_token,
            'WHATSAPP_BUSINESS_ACCOUNT_ID': business_account_id,
            'WHATSAPP_APP_ID': app_id,
        })
        
        print("✅ WhatsApp credentials configured")
        
    def configure_webhook_urls(self):
        """Configure webhook URLs"""
        self.print_step(3, "Configure Webhook URLs")
        
        print("Configure webhook URLs for WhatsApp integration:")
        print()
        
        # Production webhook URL
        webhook_url = self.get_user_input(
            "Enter your production webhook URL (e.g., https://yourdomain.com/api/whatsapp/webhook/)",
            os.getenv('WHATSAPP_WEBHOOK_URL', '')
        )
        
        # Production verify URL
        webhook_verify_url = self.get_user_input(
            "Enter your production verify URL (e.g., https://yourdomain.com/api/whatsapp/verify/)",
            os.getenv('WHATSAPP_WEBHOOK_VERIFY_URL', '')
        )
        
        # Development URLs (with defaults)
        dev_webhook_url = self.get_user_input(
            "Enter your development webhook URL",
            os.getenv('WHATSAPP_DEV_WEBHOOK_URL', 'http://localhost:8000/api/whatsapp/webhook/')
        )
        
        dev_verify_url = self.get_user_input(
            "Enter your development verify URL",
            os.getenv('WHATSAPP_DEV_VERIFY_URL', 'http://localhost:8000/api/whatsapp/verify/')
        )
        
        # Update .env file
        self.update_env_file({
            'WHATSAPP_WEBHOOK_URL': webhook_url,
            'WHATSAPP_WEBHOOK_VERIFY_URL': webhook_verify_url,
            'WHATSAPP_DEV_WEBHOOK_URL': dev_webhook_url,
            'WHATSAPP_DEV_VERIFY_URL': dev_verify_url,
        })
        
        print("✅ Webhook URLs configured")
        
    def update_env_file(self, updates):
        """Update .env file with new values"""
        if not self.config_file.exists():
            print("❌ .env file not found!")
            return
            
        # Read current .env file
        with open(self.config_file, 'r') as f:
            lines = f.readlines()
            
        # Update values
        updated_lines = []
        updated_keys = set()
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                updated_lines.append(line)
                continue
                
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                
                if key in updates:
                    updated_lines.append(f"{key}={updates[key]}")
                    updated_keys.add(key)
                else:
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
                
        # Add new keys that weren't in the original file
        for key, value in updates.items():
            if key not in updated_keys:
                updated_lines.append(f"{key}={value}")
                
        # Write back to .env file
        with open(self.config_file, 'w') as f:
            f.write('\n'.join(updated_lines))
            
    def test_whatsapp_connection(self):
        """Test WhatsApp API connection"""
        self.print_step(4, "Test WhatsApp API Connection")
        
        # Reload environment variables
        load_dotenv()
        
        phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        
        if not phone_number_id or not access_token:
            print("❌ WhatsApp credentials not configured!")
            return False
            
        try:
            # Test API connection
            url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            print("Testing WhatsApp API connection...")
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ WhatsApp API connection successful!")
                print(f"   Phone Number: {data.get('display_phone_number', 'N/A')}")
                print(f"   Verified Name: {data.get('verified_name', 'N/A')}")
                print(f"   Quality Rating: {data.get('quality_rating', 'N/A')}")
                return True
            else:
                print(f"❌ WhatsApp API connection failed!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error testing WhatsApp API connection: {str(e)}")
            return False
            
    def validate_configuration(self):
        """Validate the complete configuration"""
        self.print_step(5, "Validate Configuration")
        
        # Reload environment variables
        load_dotenv()
        
        required_vars = [
            'WHATSAPP_PHONE_NUMBER_ID',
            'WHATSAPP_ACCESS_TOKEN',
            'WHATSAPP_VERIFY_TOKEN'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
                
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        print("✅ All required environment variables are configured")
        return True
        
    def print_next_steps(self):
        """Print next steps for the user"""
        self.print_step(6, "Next Steps")
        
        print("Your WhatsApp Business API is now configured! Here's what to do next:")
        print()
        print("1. 📱 Configure Webhook in Meta Developer Console:")
        print("   - Go to your Meta Developer Console")
        print("   - Navigate to WhatsApp → Configuration")
        print("   - Set Webhook URL to: http://localhost:8000/api/whatsapp/webhook/")
        print("   - Set Verify Token to your configured verify token")
        print("   - Subscribe to these events:")
        print("     • messages")
        print("     • message_status")
        print("     • message_template_status")
        print()
        print("2. 🚀 Start your Django server:")
        print("   python manage.py runserver")
        print()
        print("3. 🌐 Test webhook verification:")
        print("   Visit: http://localhost:8000/api/whatsapp/verify/")
        print()
        print("4. 📧 Create message templates in Meta Developer Console")
        print()
        print("5. 🧪 Test sending messages through your CRM")
        print()
        print("For production deployment:")
        print("- Update webhook URLs to your production domain")
        print("- Use HTTPS for all webhook URLs")
        print("- Ensure proper SSL certificates")
        print()
        
    def run_setup(self):
        """Run the complete setup process"""
        self.print_header()
        
        # Step 1: Check prerequisites
        if not self.check_prerequisites():
            return False
            
        # Step 2: Configure credentials
        self.configure_whatsapp_credentials()
        
        # Step 3: Configure webhook URLs
        self.configure_webhook_urls()
        
        # Step 4: Validate configuration
        if not self.validate_configuration():
            return False
            
        # Step 5: Test connection
        if not self.test_whatsapp_connection():
            print("⚠️  Connection test failed, but setup can continue")
            
        # Step 6: Print next steps
        self.print_next_steps()
        
        print("🎉 WhatsApp Business API setup completed!")
        return True

def main():
    """Main function"""
    setup = WhatsAppSetup()
    
    try:
        success = setup.run_setup()
        if success:
            print("\n✅ Setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
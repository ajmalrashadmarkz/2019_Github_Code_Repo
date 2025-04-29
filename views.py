##############################################################################
#   2024-12-13 login 

from django.shortcuts import render, redirect

def login_page(request):
    return render(request,'login.html')

    ##############################################


"""
Secure Login View with Features:
- Multi-factor login attempt tracking
- Account lockout after 5 failed attempts
- 15-minute lockout duration
- Session timeout (15 minutes)
- Restricted to specific account types
- Prevents brute-force attacks
"""
from datetime import timedelta
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.utils.timezone import now
from django.conf import settings
from django.contrib.auth import get_user_model
import json
from django.utils import timezone  

User = get_user_model()



def account_login(request):
    SESSION_TIMEOUT = getattr(settings, 'SESSION_TIMEOUT', 4000)  # Default ~66 minutes
    MAX_LOGIN_ATTEMPTS = 5  # Maximum allowed login attempts
    LOCKOUT_DURATION = 15 * 60  # 15 minutes in seconds
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(email=email)
            
            # Handle previous day's login attempts
            if user.failed_attempts:
                failed_attempts = json.loads(user.failed_attempts)
                today = now().date()
                failed_attempts = [
                    attempt for attempt in failed_attempts
                    if timezone.datetime.strptime(attempt, '%Y-%m-%d').date() == today
                ]
                user.failed_attempts = json.dumps(failed_attempts)
                user.login_attempts = len(failed_attempts)
                user.save()
            
            # Check for lockout
            if user.is_locked_out and user.locked_out_until and user.locked_out_until > now():
                remaining_time = int((user.locked_out_until - now()).total_seconds())
                messages.error(request, f"Account is locked. Try again in {remaining_time // 60} minutes.")
                return render(request, 'login.html')
        
        except User.DoesNotExist:
            user = None
        
        # Authenticate the user
        authenticated_user = authenticate(request, email=email, password=password)
        
        if authenticated_user:
            # Reset security counters
            authenticated_user.login_attempts = 0
            authenticated_user.is_locked_out = False
            authenticated_user.locked_out_until = None
            authenticated_user.failed_attempts = json.dumps([])
            authenticated_user.last_login_attempt = now()
            authenticated_user.save()
            
            # Store user ID in a user-role-specific session key
            if authenticated_user.account_type and authenticated_user.account_type.id == 1:  # Admin
                request.session['adminid'] = authenticated_user.id
                redirect_url = 'admin_dashboard-dashboard'
            elif authenticated_user.account_type and authenticated_user.account_type.id == 2:  # SEO Manager
                request.session['seomanagerid'] = authenticated_user.id
                redirect_url = 'seo_dashboard-dashboard' 
            elif authenticated_user.account_type and authenticated_user.account_type.id == 3:
                request.session['partnerid'] = authenticated_user.id
                return JsonResponse({'message': 'Partner Dashboard'})
            else:
                messages.error(request, "Access denied. Invalid account type.")
                return render(request, 'login.html')
                
            # Standard login
            auth_login(request, authenticated_user)
            request.session.set_expiry(SESSION_TIMEOUT)
            request.session['last_activity'] = now().timestamp()
            
            return redirect(redirect_url)
        else:
            try:
                user = User.objects.get(email=email)
                user.login_attempts += 1
                
                failed_attempts = json.loads(user.failed_attempts) if user.failed_attempts else []
                failed_attempts.append(str(now().date()))
                user.failed_attempts = json.dumps(failed_attempts)
                
                if user.login_attempts >= MAX_LOGIN_ATTEMPTS:
                    user.is_locked_out = True
                    user.locked_out_until = now() + timedelta(seconds=LOCKOUT_DURATION)
                    messages.error(request, f"Too many failed attempts. Account locked for {LOCKOUT_DURATION // 60} minutes.")
                else:
                    messages.error(request, "Invalid email or password.")
                
                user.save()
            except User.DoesNotExist:
                messages.error(request, "Invalid email or password.")
        
        return render(request, 'login.html')
    
    # Check for session timeout
    if request.user.is_authenticated:
        last_activity = request.session.get('last_activity')
        if last_activity and now().timestamp() - last_activity > SESSION_TIMEOUT:
            logout(request)
            messages.warning(request, "Session expired due to inactivity. Please log in again.")
    
    return render(request, 'login.html')


################################################################################

from django.http import JsonResponse
from .models import AccountType
from django.utils.translation import gettext as _



def create_partner_account_type(request):
    print("####################")
    
    return JsonResponse({'message': 'Please Contact Admin'})

    # try:
    #     # Create partner account type
    #     partner_type = AccountType.objects.create(
    #         type="Partner",
    #         description="""
    #         Partner account type for business collaborators.
    #         Access Levels:
    #         - Partnership dashboard
    #         - Business analytics
    #         - Resource management
    #         - Collaboration tools
    #         """.strip(),
    #         is_active=True
    #     )
        
    #     # Success response
    #     return JsonResponse({
    #         'status': 'success',
    #         'message': _('Partner account type created successfully'),
    #         'data': {
    #             'id': partner_type.id,
    #             'type': partner_type.type,
    #             'description': partner_type.description,
    #             'is_active': partner_type.is_active
    #         }
    #     })
        
    # except Exception as e:

    #     return JsonResponse({
    #         'status': 'error',
    #         'message': str(e)
    #     }, status=400)


################################################################################

from django.http import JsonResponse
from .models import SEOManager
from .models import AdminUser,Partner
from admin_dashboard.views import admin_required


def create_admin_user(request):
    print("####################")
    
    # admin = AdminUser.objects.get(email='admin@hubnetix.com')
    # print(admin.username)
    
    # return JsonResponse({'message': 'Please Contact Admin'})

    # email = request.POST.get('email', 'admin@example.com')
    # username = request.POST.get('username', 'admin123')
    # password = request.POST.get('password', 'SecurePass123!')
    # first_name = request.POST.get('first_name', 'Admin')
    # last_name = request.POST.get('last_name', 'User')
    # admin_level = request.POST.get('admin_level', 1)

    # admin_user = AdminUser.objects.create_user(
    #     email=email,
    #     username=username,
    #     password=password,
    #     first_name=first_name,
    #     last_name=last_name,
    #     admin_level=admin_level
    # )
    # return JsonResponse({'message': 'Admin user created successfully', 'user_id': admin_user.id})




    # email = request.POST.get('email', 'seo@hubnetix.com')
    # username = request.POST.get('username', 'seoexpert')
    # password = request.POST.get('password', 'admin@123')
    # first_name = request.POST.get('first_name', 'SEO')
    # last_name = request.POST.get('last_name', 'Expert')
    # managed_domains = request.POST.getlist('managed_domains', ['hubnetix.com'])
    # report_frequency = request.POST.get('report_frequency', 'weekly')
    
    # seo_manager = SEOManager.objects.create_user(
    #     email=email,
    #     username=username,
    #     password=password,
    #     first_name=first_name,
    #     last_name=last_name,
    #     managed_domains=managed_domains,
    #     report_frequency=report_frequency
    # )
    # return JsonResponse({'message': 'User created successfully', 'user_id': seo_manager.id})




    # Get data from POST request with default values
    email = request.POST.get('email', 'partner_1@hubnetix.com')
    username = request.POST.get('username', 'partner123_1')
    password = request.POST.get('password', 'admin@123_1')
    first_name = request.POST.get('first_name', 'Partner_1')
    last_name = request.POST.get('last_name', 'User_1')
    partner_company_name = request.POST.get('partner_company_name', 'Partner Company_1')  
    business_type = request.POST.get('business_type', 'Technology')
    partnership_level = request.POST.get('partnership_level', 'BRONZE')
    
    try:
        # Create the partner user using create_user method
        partner = Partner.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            partner_company_name=partner_company_name,
            business_type=business_type,
            partnership_level=partnership_level
        )
        
        return JsonResponse({
            'message': 'Partner user created successfully',
            'user_id': partner.id,
            'company': partner.partner_company_name,
            'partnership_level': partner.partnership_level
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Failed to create partner user'
        }, status=400)













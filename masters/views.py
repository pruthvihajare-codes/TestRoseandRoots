import uuid
import os
import json
import logging
from decimal import Decimal, InvalidOperation

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, DatabaseError
from django.conf import settings
from django.utils.text import slugify

from rose_and_roots.access_control import no_direct_access
from accounts.models import *
from masters.models import *
from rose_and_roots.encryption import *

logger = logging.getLogger(__name__)

@no_direct_access
@login_required
def admin_dashboard(request):
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if not request.session.session_key:
            messages.error(request, 'Your session has expired. Please login again.')
            return redirect('/')
        
        # Check if user has admin role
        if not hasattr(request.user, 'role_id') or request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        context = {
            "page_title": "Admin Dashboard",
            "user": request.user,
            "session_key": request.session.session_key
        }

        return render(request, "masters/admin_dashboard.html", context)

    except Exception as e:
        logger.exception("Unexpected error in admin_dashboard")
        messages.error(request, "Something went wrong.")
        return redirect('login')
    
@no_direct_access
@login_required
def dashboard(request):
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if not request.session.session_key:
            messages.error(request, 'Your session has expired. Please login again.')
            return redirect('/')
        
        # Check if user has admin role
        if not hasattr(request.user, 'role_id') or request.user.role_id != 2:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        context = {
            "page_title": "Dashboard",
            "user": request.user,
            "session_key": request.session.session_key
        }

        return render(request, "masters/dashboard.html", context)

    except Exception as e:
        logger.exception("Unexpected error in dashboard")
        messages.error(request, "Something went wrong.")
        return render(request, "masters/dashboard.html")

@no_direct_access
@login_required
@transaction.atomic
def add_bouquet(request):
    """
    Add new bouquet with images and occasions
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if not request.session.session_key:
            messages.error(request, 'Your session has expired. Please login again.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # GET request - display form
        if request.method == 'GET':
            # Get all active occasions for selection
            occasions = Occasion.objects.filter(is_active=1).order_by('name')
            
            # Get all active vendors
            vendors = Vendor.objects.filter(is_active=1).order_by('vendor_name')
            
            context = {
                'occasions': occasions,
                'vendors': vendors,
                'selected_occasions': [],  # Empty list for new form
            }
            return render(request, 'masters/add_bouquet.html', context)
        
        if request.method == 'POST':

            bouquet_name = request.POST.get('bouquet_name', '').strip()
            short_description = request.POST.get('short_description', '').strip()
            description = request.POST.get('description', '').strip()
            delivery_info = request.POST.get('delivery_info', '').strip()
            instruction_text = request.POST.get('instruction_text', '').strip()
            price = request.POST.get('price', 0)
            discount = request.POST.get('discount', 0)
            vendor_id = request.POST.get('vendor')
            occasion_ids_str = request.POST.get('occasions', '')
            occasion_ids = [id for id in occasion_ids_str.split(',') if id]
            is_active = request.POST.get('is_active', '1')

            errors = {}

            # ---------------- VALIDATION ---------------- #

            if not bouquet_name:
                errors['bouquet_name'] = 'Bouquet name is required.'

            if not short_description:
                errors['short_description'] = 'Short description is required.'

            if not description:
                errors['description'] = 'Full description is required.'

            try:
                price_decimal = Decimal(price)
                if price_decimal <= 0:
                    errors['price'] = 'Price must be greater than 0.'
            except (InvalidOperation, TypeError):
                errors['price'] = 'Invalid price format.'

            try:
                discount_int = int(discount) if discount else 0
                if discount_int < 0 or discount_int > 100:
                    errors['discount'] = 'Discount must be between 0 and 100.'
            except ValueError:
                errors['discount'] = 'Invalid discount value.'

            if not occasion_ids:
                errors['occasions'] = 'Select at least one occasion.'

            images = request.FILES.getlist('bouquet_images')

            if not images:
                errors['images'] = 'Upload at least one image.'
            elif len(images) > 5:
                errors['images'] = 'Maximum 5 images allowed.'

            if errors:
                for error in errors.values():
                    messages.error(request, error)
                return render(request, 'masters/add_bouquet.html')

            # ---------------- SAVE DATA ---------------- #

            try:
                with transaction.atomic():

                    # Calculate discount price
                    discount_price = None
                    if discount_int > 0:
                        discount_price = price_decimal - (price_decimal * discount_int / 100)

                    # Generate unique slug
                    base_slug = slugify(bouquet_name)
                    slug = base_slug
                    counter = 1
                    while Bouquet.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1

                    # Create bouquet
                    bouquet = Bouquet.objects.create(
                        name=bouquet_name,
                        slug=slug,
                        short_description=short_description,
                        description=description,
                        delivery_info=delivery_info,
                        instruction_text=instruction_text,
                        price=price_decimal,
                        discount_percent=discount_int,
                        discount_price=discount_price,
                        is_active=1 if is_active == '1' else 0,
                        same_day_available=0,
                        is_featured=0
                    )

                    # ---------------- IMAGE SAVE ---------------- #

                    allowed_types = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']

                    # Folder: bouquets/<bouquet_id>/
                    relative_path = f"bouquets/{bouquet.id}/"
                    upload_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                    os.makedirs(upload_path, exist_ok=True)

                    for image_file in images:

                        if image_file.size > 6 * 1024 * 1024:
                            continue

                        if image_file.content_type not in allowed_types:
                            continue

                        ext = os.path.splitext(image_file.name)[1]
                        unique_filename = f"{uuid.uuid4().hex}{ext}"

                        full_path = os.path.join(upload_path, unique_filename)

                        with open(full_path, 'wb+') as destination:
                            for chunk in image_file.chunks():
                                destination.write(chunk)

                        db_image_path = f"{relative_path}{unique_filename}"

                        BouquetImage.objects.create(
                            bouquet=bouquet,
                            image_name=image_file.name,
                            image_path=db_image_path,
                            is_active=1,
                            created_by=request.user.id
                        )

                    # ---------------- OCCASIONS ---------------- #

                    occasions = Occasion.objects.filter(
                        id__in=occasion_ids,
                        is_active=1
                    )

                    for occasion in occasions:
                        BouquetOccasion.objects.create(
                            bouquet=bouquet,
                            occasion=occasion
                        )

                messages.success(request, "Bouquet created successfully!")
                return redirect('admin_dashboard')

            except Exception as e:
                logger.exception(str(e))
                messages.error(request, "Something went wrong.")
                return render(request, 'masters/add_bouquet.html')

    except Exception as e:
        logger.exception(f"Unexpected error in add_bouquet: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('add_bouquet')

@no_direct_access
@login_required
@transaction.atomic
def vendor_list(request):
    """
    Display list of all vendors
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Get all vendors
        vendors = Vendor.objects.all().order_by('-created_at')
        vendor_list = []
        for ven in vendors:
            ven.encrypted_id = enc(str(ven.id))  # Add encrypted ID as attribute
            vendor_list.append(ven)
        
        context = {
            'vendors': vendor_list,
        }
        return render(request, 'masters/vendor_list.html', context)
        
    except Exception as e:
        logger.exception(f"Error in vendor_list: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('admin_dashboard')

@no_direct_access
@login_required
@transaction.atomic
def add_vendor(request):
    """
    Add new vendor
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Get all delivery pincodes for dropdown - CHANGE HERE
        delivery_pincodes = DeliveryPincode.objects.filter(is_active=1).order_by('pincode')
        pincode_dict = {p.pincode: p.place_name for p in delivery_pincodes}
        
        # GET request - display form
        if request.method == 'GET':
            context = {
                'delivery_pincodes': pincode_dict,  # Now passing as dict, not JSON
                'form_data': request.session.pop('form_data', {}),
            }
            return render(request, 'masters/add_vendor.html', context)
        
        # POST request - process form
        if request.method == 'POST':
            
            vendor_name = request.POST.get('vendor_name', '').strip()
            phone_no = request.POST.get('phone_no', '').strip()
            email = request.POST.get('email', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            vendor_address = request.POST.get('vendor_address', '').strip()
            is_active = request.POST.get('is_active', '0')
            
            errors = {}
            
            # ---------------- VALIDATION ---------------- #
            
            if not vendor_name:
                errors['vendor_name'] = 'Vendor name is required.'
            elif len(vendor_name) < 3:
                errors['vendor_name'] = 'Vendor name must be at least 3 characters.'
            
            if not phone_no:
                errors['phone_no'] = 'Phone number is required.'
            elif not phone_no.isdigit() or len(phone_no) != 10:
                errors['phone_no'] = 'Please enter a valid 10-digit mobile number.'
            
            if email and '@' not in email:
                errors['email'] = 'Please enter a valid email address.'
            
            if not pincode:
                errors['pincode'] = 'Pincode is required.'
            else:
                # Check if pincode exists in delivery_pincodes
                if pincode not in pincode_dict:
                    errors['pincode'] = 'Invalid pincode selected.'
            
            if errors:
                # Store form data in session
                request.session['form_data'] = request.POST.dict()
                for error in errors.values():
                    messages.error(request, error)
                return redirect('add_vendor')
            
            # ---------------- SAVE DATA ---------------- #
            
            try:
                with transaction.atomic():
                    
                    # Get area_name from pincode_dict - CHANGE HERE
                    area_name = pincode_dict.get(pincode, '')
                    
                    # Create vendor
                    vendor = Vendor.objects.create(
                        vendor_name=vendor_name,
                        phone_no=phone_no,
                        email=email if email else None,
                        area_name=area_name,  # Now using place name from delivery_pincodes
                        pincode=pincode,
                        vendor_address=vendor_address,
                        is_active=1 if is_active == '1' else 0,
                        created_by=request.user.email or 'admin'
                    )
                    
                messages.success(request, f"Vendor '{vendor_name}' created successfully!")
                return redirect('vendor_list')
                
            except Exception as e:
                logger.exception(f"Error creating vendor: {str(e)}")
                messages.error(request, "Something went wrong while saving the vendor.")
                return redirect('add_vendor')
                
    except Exception as e:
        logger.exception(f"Unexpected error in add_vendor: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('add_vendor')

@no_direct_access
@login_required
def view_vendor(request):
    """
    View vendor details using encrypted ID from query parameter
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Get encrypted ID from query parameter
        encrypted_id = request.GET.get('vendor_id')
        
        if not encrypted_id:
            messages.error(request, 'Vendor ID is required.')
            return redirect('vendor_list')
        
        # Decrypt the vendor ID
        decrypted_id = dec(str(encrypted_id))
        
        # Get vendor
        vendor = get_object_or_404(Vendor, id=decrypted_id)
        
        context = {
            'vendor': vendor,
            'encrypted_id': encrypted_id,
        }
        return render(request, 'masters/view_vendor.html', context)
        
    except Exception as e:
        logger.exception(f"Error in view_vendor: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('vendor_list')

@no_direct_access
@login_required
@transaction.atomic
def edit_vendor(request):
    """
    Edit vendor details using encrypted ID from query parameter
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Get encrypted ID from query parameter
        encrypted_id = request.GET.get('vendor_id')
        
        if not encrypted_id:
            messages.error(request, 'Vendor ID is required.')
            return redirect('vendor_list')
        
        # Decrypt the vendor ID
        decrypted_id = dec(str(encrypted_id))
        
        # Get vendor
        vendor = get_object_or_404(Vendor, id=decrypted_id)
        
        # Get all delivery pincodes for dropdown
        delivery_pincodes = DeliveryPincode.objects.filter(is_active=1).order_by('pincode')
        pincode_dict = {p.pincode: p.place_name for p in delivery_pincodes}
        
        # GET request - display form
        if request.method == 'GET':
            context = {
                'vendor': vendor,
                'delivery_pincodes': pincode_dict,
                'encrypted_id': encrypted_id,  # Pass back to template for form action
            }
            return render(request, 'masters/edit_vendor.html', context)
        
        # POST request - process form
        if request.method == 'POST':
            
            vendor_name = request.POST.get('vendor_name', '').strip()
            phone_no = request.POST.get('phone_no', '').strip()
            email = request.POST.get('email', '').strip()
            pincode = request.POST.get('pincode', '').strip()
            vendor_address = request.POST.get('vendor_address', '').strip()
            is_active = request.POST.get('is_active', '0')
            
            errors = {}
            
            # ---------------- VALIDATION ---------------- #
            
            if not vendor_name:
                errors['vendor_name'] = 'Vendor name is required.'
            elif len(vendor_name) < 3:
                errors['vendor_name'] = 'Vendor name must be at least 3 characters.'
            
            if not phone_no:
                errors['phone_no'] = 'Phone number is required.'
            elif not phone_no.isdigit() or len(phone_no) != 10:
                errors['phone_no'] = 'Please enter a valid 10-digit mobile number.'
            
            if email and '@' not in email:
                errors['email'] = 'Please enter a valid email address.'
            
            if not pincode:
                errors['pincode'] = 'Pincode is required.'
            else:
                # Check if pincode exists in delivery_pincodes
                if pincode not in pincode_dict:
                    errors['pincode'] = 'This pincode is not in our delivery network.'
            
            if errors:
                for error in errors.values():
                    messages.error(request, error)
                return redirect(f'{request.path}?vendor_id={encrypted_id}')
            
            # ---------------- UPDATE DATA ---------------- #
            
            try:
                with transaction.atomic():
                    
                    # Get area_name from pincode_dict
                    area_name = pincode_dict.get(pincode, '')
                    
                    # Update vendor
                    vendor.vendor_name = vendor_name
                    vendor.phone_no = phone_no
                    vendor.email = email if email else None
                    vendor.area_name = area_name
                    vendor.pincode = pincode
                    vendor.vendor_address = vendor_address
                    vendor.is_active = 1 if is_active == '1' else 0
                    
                    vendor.save()
                    
                messages.success(request, f"Vendor '{vendor_name}' updated successfully!")
                return redirect('vendor_list')
                
            except Exception as e:
                logger.exception(f"Error updating vendor: {str(e)}")
                messages.error(request, "Something went wrong while updating the vendor.")
                return redirect(f'{request.path}?vendor_id={encrypted_id}')
                
    except Exception as e:
        logger.exception(f"Unexpected error in edit_vendor: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('vendor_list')

@no_direct_access
@login_required
@transaction.atomic
def delete_vendor(request):
    """
    Delete vendor
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to perform this action.')
            return redirect('/')
        
        if request.method == 'POST':
            encrypted_vendor_id = request.POST.get('vendor_id')
            
            try:
                # Decrypt the vendor ID
                vendor_id = dec(str(encrypted_vendor_id))
                vendor = Vendor.objects.get(id=vendor_id)
                
                vendor_name = vendor.vendor_name
                vendor.delete()
                
                messages.success(request, f"Vendor '{vendor_name}' deleted successfully!")
                
            except Vendor.DoesNotExist:
                messages.error(request, 'Vendor not found.')
            except Exception as e:
                logger.exception(f"Error deleting vendor: {str(e)}")
                messages.error(request, 'Something went wrong while deleting the vendor.')
        
        return redirect('vendor_list')
        
    except Exception as e:
        logger.exception(f"Unexpected error in delete_vendor: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('vendor_list')
    
@no_direct_access
@login_required
@transaction.atomic
def occasion_list(request):
    """
    Display list of all occasions
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Get all occasions
        occasions = Occasion.objects.all().order_by('-created_at')
        occasion_list = []
        for occ in occasions:
            occ.encrypted_id = enc(str(occ.id))
            occasion_list.append(occ)
        
        context = {
            'occasions': occasion_list,
        }
        return render(request, 'masters/occasion_list.html', context)
        
    except Exception as e:
        logger.exception(f"Error in occasion_list: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('admin_dashboard')


@no_direct_access
@login_required
@transaction.atomic
def add_occasion(request):
    """
    Add new occasion
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # GET request - display form
        if request.method == 'GET':
            context = {
                'form_data': request.session.pop('form_data', {}),
            }
            return render(request, 'masters/add_occasion.html', context)
        
        # POST request - process form
        if request.method == 'POST':
            
            name = request.POST.get('name', '').strip()
            icon = request.POST.get('icon', '').strip()
            is_active = request.POST.get('is_active', '0')
            
            errors = {}
            
            # ---------------- VALIDATION ---------------- #
            
            if not name:
                errors['name'] = 'Occasion name is required.'
            elif len(name) < 3:
                errors['name'] = 'Occasion name must be at least 3 characters.'
            else:
                # Check if occasion with same name already exists
                if Occasion.objects.filter(name__iexact=name).exists():
                    errors['name'] = 'An occasion with this name already exists.'
            
            if errors:
                # Store form data in session
                request.session['form_data'] = request.POST.dict()
                for error in errors.values():
                    messages.error(request, error)
                return redirect('add_occasion')
            
            # ---------------- SAVE DATA ---------------- #
            
            try:
                with transaction.atomic():
                    
                    # Generate slug from name
                    from django.utils.text import slugify
                    base_slug = slugify(name)
                    slug = base_slug
                    counter = 1
                    while Occasion.objects.filter(slug=slug).exists():
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                    
                    # Create occasion
                    occasion = Occasion.objects.create(
                        name=name,
                        slug=slug,
                        icon=icon if icon else None,
                        is_active=1 if is_active == '1' else 0
                    )
                    
                messages.success(request, f"Occasion '{name}' created successfully!")
                return redirect('occasion_list')
                
            except Exception as e:
                logger.exception(f"Error creating occasion: {str(e)}")
                messages.error(request, "Something went wrong while saving the occasion.")
                return redirect('add_occasion')
                
    except Exception as e:
        logger.exception(f"Unexpected error in add_occasion: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('add_occasion')


@no_direct_access
@login_required
def view_occasion(request):
    """
    View occasion details using encrypted ID from query parameter
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Get encrypted ID from query parameter
        encrypted_id = request.GET.get('occasion_id')
        
        if not encrypted_id:
            messages.error(request, 'Occasion ID is required.')
            return redirect('occasion_list')
        
        # Decrypt the occasion ID
        decrypted_id = dec(str(encrypted_id))
        
        # Get occasion
        occasion = get_object_or_404(Occasion, id=decrypted_id)
        
        context = {
            'occasion': occasion,
            'encrypted_id': encrypted_id,
        }
        return render(request, 'masters/view_occasion.html', context)
        
    except Exception as e:
        logger.exception(f"Error in view_occasion: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('occasion_list')


@no_direct_access
@login_required
@transaction.atomic
def edit_occasion(request):
    """
    Edit occasion details using encrypted ID from query parameter
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('/')
        
        # Get encrypted ID from query parameter
        encrypted_id = request.GET.get('occasion_id')
        
        if not encrypted_id:
            messages.error(request, 'Occasion ID is required.')
            return redirect('occasion_list')
        
        # Decrypt the occasion ID
        decrypted_id = dec(str(encrypted_id))
        
        # Get occasion
        occasion = get_object_or_404(Occasion, id=decrypted_id)
        
        # GET request - display form
        if request.method == 'GET':
            context = {
                'occasion': occasion,
                'encrypted_id': encrypted_id,
            }
            return render(request, 'masters/edit_occasion.html', context)
        
        # POST request - process form
        if request.method == 'POST':
            
            name = request.POST.get('name', '').strip()
            icon = request.POST.get('icon', '').strip()
            is_active = request.POST.get('is_active', '0')
            
            errors = {}
            
            # ---------------- VALIDATION ---------------- #
            
            if not name:
                errors['name'] = 'Occasion name is required.'
            elif len(name) < 3:
                errors['name'] = 'Occasion name must be at least 3 characters.'
            else:
                # Check if another occasion with same name exists (excluding current)
                if Occasion.objects.filter(name__iexact=name).exclude(id=decrypted_id).exists():
                    errors['name'] = 'An occasion with this name already exists.'
            
            if errors:
                for error in errors.values():
                    messages.error(request, error)
                return redirect(f'{request.path}?occasion_id={encrypted_id}')
            
            # ---------------- UPDATE DATA ---------------- #
            
            try:
                with transaction.atomic():
                    
                    # Update slug if name changed
                    from django.utils.text import slugify
                    if occasion.name != name:
                        base_slug = slugify(name)
                        slug = base_slug
                        counter = 1
                        while Occasion.objects.filter(slug=slug).exclude(id=decrypted_id).exists():
                            slug = f"{base_slug}-{counter}"
                            counter += 1
                        occasion.slug = slug
                    
                    # Update occasion
                    occasion.name = name
                    occasion.icon = icon if icon else None
                    occasion.is_active = 1 if is_active == '1' else 0
                    
                    occasion.save()
                    
                messages.success(request, f"Occasion '{name}' updated successfully!")
                return redirect('occasion_list')
                
            except Exception as e:
                logger.exception(f"Error updating occasion: {str(e)}")
                messages.error(request, "Something went wrong while updating the occasion.")
                return redirect(f'{request.path}?occasion_id={encrypted_id}')
                
    except Exception as e:
        logger.exception(f"Unexpected error in edit_occasion: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('occasion_list')


@no_direct_access
@login_required
@transaction.atomic
def delete_occasion(request):
    """
    Delete occasion
    Only accessible to Admin (role_id=1)
    """
    try:
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access the dashboard.')
            return redirect('/')
        
        if request.user.role_id != 1:
            messages.error(request, 'You do not have permission to perform this action.')
            return redirect('/')
        
        if request.method == 'POST':
            encrypted_occasion_id = request.POST.get('occasion_id')
            
            if not encrypted_occasion_id:
                messages.error(request, 'Occasion ID is required.')
                return redirect('occasion_list')
            
            try:
                # Decrypt the occasion ID
                occasion_id = dec(str(encrypted_occasion_id))
                occasion = Occasion.objects.get(id=occasion_id)
                
                occasion_name = occasion.name
                occasion.delete()
                
                messages.success(request, f"Occasion '{occasion_name}' deleted successfully!")
                
            except Occasion.DoesNotExist:
                messages.error(request, 'Occasion not found.')
            except Exception as e:
                logger.exception(f"Error deleting occasion: {str(e)}")
                messages.error(request, 'Something went wrong while deleting the occasion.')
        
        return redirect('occasion_list')
        
    except Exception as e:
        logger.exception(f"Unexpected error in delete_occasion: {str(e)}")
        messages.error(request, 'Something went wrong. Please try again later.')
        return redirect('occasion_list')
########################################################################################################################
########################################################################################################################
########################################################################################################################
# 2025-01-02

from django.http import Http404
from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import EditProductForm

def handle_images(request, product):
    """
    Handle product image uploads and deletions
    """
    # Delete selected images
    image_ids_to_remove = request.POST.getlist('images_to_remove', [])
    ProductImage.objects.filter(id__in=image_ids_to_remove, product=product).delete()

    # Add new images
    for img in request.FILES.getlist('additional_images'):
        ProductImage.objects.create(product=product, product_image=img)

def handle_documents(request, product):
    """
    Handle product document uploads and deletions
    """
    # Delete selected documents
    doc_ids_to_remove = request.POST.getlist('documents_to_remove', [])
    ProductDocument.objects.filter(id__in=doc_ids_to_remove, product=product).delete()

    # Add new documents
    for doc in request.FILES.getlist('additional_documents'):
        ProductDocument.objects.create(
            product=product,
            title=doc.name.split('.')[0],
            document=doc
        )

def get_product_details(product_id):
    """
    Get all details related to a product including specifications, images, and documents
    """
    try:
        product = Product.objects.get(id=product_id)
        specifications = list(product.specifications.values(
            'specification_title',
            'specification'
        ))
        
        # Convert specifications to list format
        spec_list = [
            {
                'title': spec['specification_title'],
                'value': spec['specification']
            } for spec in specifications
        ]
        
        images = product.images.all()
        documents = product.documents.all()
        
        return {
            "product": product,
            "specifications": spec_list,
            "images": images,
            "documents": documents
        }
    except Product.DoesNotExist:
        raise Http404("Product not found")

def process_specifications(post_data):
    """
    Process specifications from POST data and return as list
    Handles multiple specifications with same title
    """
    specifications = []
    i = 0
    
    while True:
        title_key = f'specification_title_{i}'
        value_key = f'specification_{i}'
        
        # Break if no more specifications found
        if title_key not in post_data or value_key not in post_data:
            break
            
        title = post_data.get(title_key)
        value = post_data.get(value_key)
        
        # Only add if both title and value are present
        if title and value:
            specifications.append({
                'title': title,
                'value': value
            })
            
        i += 1
    
    return specifications

@transaction.atomic
def process_edit_form(request, product_id):
    """
    Process the edit form submission with transaction atomic
    """
    try:
        product = Product.objects.get(id=product_id)
        form = EditProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            # Save the main product data
            product = form.save()
            
            # Process specifications
            specifications = process_specifications(request.POST)
            print("Processed specifications:", specifications)  # Debug log
            
            # Delete existing specifications
            product.specifications.all().delete()

            # Create new specifications
            for spec in specifications:
                ProductSpecification.objects.create(
                    product=product,
                    specification_title=spec['title'],
                    specification=spec['value']
                )
            
            # Handle media files
            handle_images(request, product)
            handle_documents(request, product)

            return {"success": True, "message": "Product updated successfully."}
        else:
            return {"success": False, "errors": form.errors}
            
    except Product.DoesNotExist:
        return {"success": False, "errors": "Product not found"}
    except Exception as e:
        return {"success": False, "errors": str(e)}

@admin_required
def product_edit(request, pk):
    """
    View function to handle product editing
    """
    if request.method == 'POST':
        result = process_edit_form(request, pk)
        
        if result["success"]:
            messages.success(request, result["message"])
            return redirect('admin_dashboard-product_details', pk=pk)
        else:
            # If error, get product details and show form with errors
            product_details = get_product_details(pk)
            form = EditProductForm(instance=product_details["product"])
            context = {
                'form': form,
                'errors': result.get("errors", None),
                'existing_images': product_details["images"],
                'existing_documents': product_details["documents"],
                'specifications_json': product_details["specifications"],
            }
    else:
        # GET request - show edit form
        product_details = get_product_details(pk)
        form = EditProductForm(instance=product_details["product"])
        context = {
            'form': form,
            'product': product_details["product"],
            'is_edit': True,
            'existing_images': product_details["images"],
            'existing_documents': product_details["documents"],
            'specifications_json': product_details["specifications"],
        }

    return render(request, 'product_edit_form.html', context)






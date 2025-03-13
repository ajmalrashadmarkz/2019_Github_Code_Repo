#################################################################################################
#################################################################################################
#################################################################################################

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ProductForm
from .models import ProductImage,ProductDocument,ProductSpecification
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse

@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            try:

                product = form.save(commit=True)


                # images = request.FILES.getlist('additional_images')
                # for image in images:
                #     ProductImage.objects.create(product=product, product_image=image)

                messages.success(request, f"Product '{product.name}' created successfully!")
                return redirect('admin_dashboard-products_list')
            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")
        else:

            for field, errors in form.errors.items():
                field_label = form.fields[field].label or field
                for error in errors:
                    messages.error(request, f"{field_label}: {error}")
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {
        'form': form,
        'edit_mode': False,
    })

#####################################################################################################



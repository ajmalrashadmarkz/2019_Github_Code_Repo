from django import forms
from .models import Product, Category, ProductImage, ProductDocument
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category, ProductImage, ProductDocument, ProductSpecification
import json
from django.db.models import Q


class ProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset = Category.objects.filter(deleted_at__isnull=True).filter(
            ~Q(id__in=Category.objects.filter(parent__isnull=False).values_list('parent', flat=True))
        ),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'multiple': 'multiple'
        }),
        required=True,
        help_text='Select one or more categories for this product'
    )

    additional_images = forms.FileField(
        required=False,
        label='Additional Images',
        help_text='Select multiple images for the product gallery'
    )

    additional_documents = forms.FileField(
        required=False,
        label='Additional Documents',
        help_text='Select multiple documents for the product'
    )

    specifications = forms.JSONField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Product
        fields = [
            'name',
            'short_description',
            'detailed_description',
            'main_image',
            'quantity_in_stock',
            'categories',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter product name'}),
            'short_description': forms.TextInput(attrs={'placeholder': 'Enter short description'}),
            'detailed_description': forms.Textarea(attrs={'placeholder': 'Enter detailed description'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'placeholder': 'Enter stock quantity'}),
        }
        labels = {
            'name': 'Product Name',
            'short_description': 'Short Description',
            'detailed_description': 'Detailed Description',
            'main_image': 'Main Image',
            'quantity_in_stock': 'Quantity in Stock',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['short_description'].required = True
        self.fields['detailed_description'].required = True
        self.fields['main_image'].required = True

        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif not isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs.update({'class': 'form-control'})
            if self.errors.get(field_name):
                field.widget.attrs.update({'class': 'form-control is-invalid'})

        # Configure additional fields for multi-upload
        self.fields['additional_images'].widget.attrs.update({
            'class': 'form-control',
            'multiple': True,
            'accept': 'image/*'
        })
        self.fields['additional_documents'].widget.attrs.update({
            'class': 'form-control',
            'multiple': True,
            'accept': '.pdf,.doc,.docx,.txt,.xls,.xlsx,.csv,.ppt,.pptx'
        })

    def clean_name(self):
        """
        Custom validation for product name uniqueness
        """
        name = self.cleaned_data.get('name')
        if not name:
            return name

        # Get the current instance if we're editing
        instance = getattr(self, 'instance', None)
        
        # Build the query to check for duplicate names
        query = Product.objects.filter(name__iexact=name)
        
        # If we're editing, exclude the current instance from the check
        if instance and instance.pk:
            query = query.exclude(pk=instance.pk)
            
        # If we found any other products with this name
        if query.exists():
            raise ValidationError("Product with this Name already exists.")
            
        return name

    def clean_specifications(self):
        """
        Validate specifications format and content
        """
        specs = self.cleaned_data.get('specifications')
        if not specs:
            return []

        try:
            if isinstance(specs, str):
                specs = json.loads(specs)
            
            # Convert dict format to list format if necessary
            if isinstance(specs, dict):
                specs = [{'title': k, 'value': v} for k, v in specs.items()]
            
            # Validate each specification
            for spec in specs:
                if not isinstance(spec, dict):
                    raise ValidationError("Invalid specification format")
                
                if 'title' not in spec or 'value' not in spec:
                    raise ValidationError("Specifications must have both title and value")
                
                if not spec['title'].strip() or not spec['value'].strip():
                    raise ValidationError("Specification title and value cannot be empty")
                
        except json.JSONDecodeError:
            raise ValidationError("Invalid specification format")
        except (KeyError, AttributeError):
            raise ValidationError("Invalid specification structure")

        return specs

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            # Handle specifications
            specs_data = self.cleaned_data.get('specifications', [])
            
            # Delete existing specifications
            ProductSpecification.objects.filter(product=instance).delete()

            # Create new specifications
            for spec in specs_data:
                ProductSpecification.objects.create(
                    product=instance,
                    specification_title=spec['title'].strip(),
                    specification=spec['value'].strip()
                )

            # Handle categories
            instance.categories.clear()
            instance.categories.add(*self.cleaned_data['categories'])

            # Handle images
            images = self.files.getlist('additional_images')
            for image in images:
                ProductImage.objects.create(
                    product=instance,
                    product_image=image
                )

            # Handle documents
            documents = self.files.getlist('additional_documents')
            for document in documents:
                ProductDocument.objects.create(
                    product=instance,
                    title=document.name.split('.')[0],
                    document=document
                )

        return instance
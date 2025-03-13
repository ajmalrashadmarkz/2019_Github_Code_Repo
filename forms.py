
from django import forms
from .models import Product, Category, ProductImage, ProductDocument
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category, ProductImage, ProductDocument, ProductSpecification
import json
from django.db.models import Q

class ProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        # queryset=Category.objects.filter(deleted_at__isnull=True),
        queryset = Category.objects.filter(deleted_at__isnull=True).filter(~Q(id__in=Category.objects.filter(parent__isnull=False).values_list('parent', flat=True))),
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
            #'detailed_description': SummernoteWidget(),
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

    def clean_specifications(self):
        specs = self.cleaned_data.get('specifications')
        if specs:
            if not isinstance(specs, dict):
                try:
                    specs = json.loads(specs)
                except json.JSONDecodeError:
                    raise ValidationError("Invalid specification format")

            for key, value in specs.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValidationError("Specifications must be text")
                if not key.strip() or not value.strip():
                    raise ValidationError("Specification keys and values cannot be empty")

        return specs or {}

    def save(self, commit=True):
        instance = super().save(commit=False)

        if commit:
            instance.save()

            specs_data = self.cleaned_data.get('specifications', {})
            if isinstance(specs_data, str):
                try:
                    specs_data = json.loads(specs_data)
                except json.JSONDecodeError:
                    specs_data = {}

            for heading, value in specs_data.items():
                if heading and value:
                    ProductSpecification.objects.create(
                        product=instance,
                        specification_title=heading.strip(),
                        specification=value.strip()
                    )

            instance.categories.clear()
            instance.categories.add(*self.cleaned_data['categories'])

            images = self.files.getlist('additional_images')
            for image in images:
                ProductImage.objects.create(product=instance, product_image=image)

            documents = self.files.getlist('additional_documents')
            for document in documents:
                ProductDocument.objects.create(
                    product=instance,
                    title=document.name.split('.')[0],
                    document=document
                )

        return instance
    












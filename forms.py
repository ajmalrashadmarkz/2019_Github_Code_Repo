

from django import forms
from django.db.models import Q
from .models import Product, ProductSpecification, Category
import json
from django.core.exceptions import ValidationError

class EditProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset = Category.objects.filter(deleted_at__isnull=True).filter(
            ~Q(id__in=Category.objects.filter(parent__isnull=False).values_list('parent', flat=True))
        ),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control select2',
            'multiple': 'multiple'
        }),
        required=True
    )
    specifications_data = forms.JSONField(  # Changed field name to match template
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Product
        fields = [
            'name', 'short_description', 'detailed_description',
            'main_image', 'quantity_in_stock', 'categories'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.TextInput(attrs={'class': 'form-control'}),
            'detailed_description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 5
            }),
            'main_image': forms.FileInput(attrs={'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        
        if instance:
            # Get all specifications for this product
            specs = instance.specifications.all()
            if specs.exists():
                # Changed to list format instead of dict
                specs_list = [
                    {
                        'title': spec.specification_title,
                        'value': spec.specification
                    }
                    for spec in specs
                ]
                self.initial['specifications_data'] = json.dumps(specs_list)

    def clean_specifications_data(self):
        specs = self.cleaned_data.get('specifications_data')
        if not specs:
            return []
            
        try:
            if isinstance(specs, str):
                specs = json.loads(specs)
            if not isinstance(specs, list):  # Changed to check for list instead of dict
                raise ValidationError("Specifications must be a valid JSON array")
            
            # Validate each specification
            for spec in specs:
                if not isinstance(spec, dict):
                    raise ValidationError("Each specification must be an object")
                if 'title' not in spec or 'value' not in spec:
                    raise ValidationError("Each specification must have a title and value")
                if not spec['title'].strip() or not spec['value'].strip():
                    raise ValidationError("Specification title and value cannot be empty")
            
            return specs
        except json.JSONDecodeError:
            raise ValidationError("Invalid specification format")

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            self.save_m2m()  # Save many-to-many fields (categories)
            
            # Handle specifications
            specs_data = self.cleaned_data.get('specifications_data', [])
            if isinstance(specs_data, str):
                specs_data = json.loads(specs_data)
            
            # Delete all existing specifications
            instance.specifications.all().delete()
            
            # Create new specifications
            for spec in specs_data:
                ProductSpecification.objects.create(
                    product=instance,
                    specification_title=spec['title'],
                    specification=spec['value']
                )
        
        return instance











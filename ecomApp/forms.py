from django import forms
from django.contrib.auth.models import User
from .models import Product


class WholesellerForm(forms.Form):
    name = forms.CharField(max_length=100)
    company_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_no = forms.CharField(max_length=15)
    address = forms.CharField(widget=forms.Textarea)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

class CustomerForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    phone_no = forms.CharField(max_length=15)
    sell_on_amazon = forms.BooleanField(required=False)
    sell_on_flipkart = forms.BooleanField(required=False)
    sell_on_meesho = forms.BooleanField(required=False)
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['id', 'user']
        labels = {
            'name': 'Product Name',
            'sku': 'Product SKU',
            'price': 'Price',
            'image': 'Image',
            'hsn_code': 'HSN Code',
            'carton_quantity': 'Carton Quantity',
            'in_stock': 'In Stock',
            'category': 'Category',
        }
        widgets = {
            'name': forms.TextInput(attrs={  # Assuming name is a text field
                'class': 'u-input',
                'placeholder': 'Enter product name',
            }),
            'sku': forms.TextInput(attrs={
                'placeholder': 'e.g. S123',
                'class': 'u-input',
            }),
            'price': forms.NumberInput(attrs={  # Assuming price is a number field
                'placeholder': 'Enter price',
                'class': 'u-input',
                'step': '0.01',  # For decimals
            }),
            'image': forms.FileInput(attrs={
                'class': 'u-input',
            }),
            'hsn_code': forms.TextInput(attrs={  # Assuming HSN code is text
                'placeholder': 'Enter HSN Code',
                'class': 'u-input',
            }),
            'carton_quantity': forms.NumberInput(attrs={  # Assuming quantity is a number
                'placeholder': 'Enter carton quantity',
                'class': 'u-input',
            }),
            'in_stock': forms.NumberInput(attrs={  # Assuming in_stock is a number
                'placeholder': 'Enter stock quantity',
                'class': 'u-input',
            }),
            'category': forms.Select(attrs={  # Assuming category is a dropdown
                'class': 'u-input',
            }),
        }

from django import forms
from .models import Feedback, ProductModel
class SearchForm(forms.Form):
    serial_number = forms.CharField(
        max_length=50,
        label="Введите серийный номер",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: A1B2C3D4E5F6'
        })
    )

class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Имя",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваше имя'
        })
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш email'
        })
    )
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Введите ваше сообщение'
        })
    )

class ProductTypeForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Название типа техники",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Например: Смартфоны'
        })
    )
    description = forms.CharField(
        label="Описание",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Добавьте описание типа техники'
        })
    )

class ProductModelForm(forms.ModelForm):
    class Meta:
        model = ProductModel
        fields = ['product_type', 'name']
        widgets = {
            'product_type': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: iPhone 15 Pro'
            })
        }
        labels = {
            'product_type': 'Тип техники',
            'name': 'Название модели'
        }

class GenerateBulkProductsForm(forms.Form):
    model = forms.ModelChoiceField(queryset=ProductModel.objects.all(), label="Модель")
    quantity = forms.IntegerField(min_value=1, max_value=1000, label="Количество товаров")

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваше имя'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите ваш email'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Введите сообщение',
                'rows': 5
            }),
        }
        labels = {
            'name': 'Имя',
            'email': 'Email',
            'message': 'Сообщение',
        }
from django.contrib import admin, messages
from django import forms
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from django.http import HttpResponse
from django.utils import timezone
from .models import ProductType, ProductModel, Product, Warranty, Movement, Feedback
from django.shortcuts import render, redirect
from django.urls import path

class GenerateBulkProductsForm(forms.Form):
    model = forms.ModelChoiceField(queryset=ProductModel.objects.all(), label="Модель")
    quantity = forms.IntegerField(min_value=1, max_value=1000, label="Количество товаров")

class BulkEditMovementForm(forms.Form):
    move_type = forms.ChoiceField(choices=Movement.MOVE_TYPES, label="Новый тип перемещения")
    location = forms.CharField(max_length=100, label="Новое местоположение")

class ProductModelInline(admin.TabularInline):
    model = ProductModel
    extra = 1

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    inlines = [ProductModelInline]
    list_display = ('name', 'description')
    search_fields = ('name',)

    def export_qr_pdf(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Выберите хотя бы один товар.", level='error')
            return

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="qr_codes_{timezone.now().date()}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        x, y = 20 * mm, height - 30 * mm

        for product in queryset:
            p.setFont("Helvetica", 10)
            p.drawString(x, y, f"{product.serial_number}")

            if product.qr_code and product.qr_code.path:
                try:
                    p.drawImage(product.qr_code.path, x + 100, y - 10, width=40 * mm, height=40 * mm)
                except Exception as e:
                    p.drawString(x, y - 10, "QR-код не найден")

            y -= 50 * mm
            if y < 50 * mm:
                p.showPage()
                y = height - 30 * mm

        p.save()
        return response

    export_qr_pdf.short_description = "Скачать PDF с QR-кодами"

@admin.register(ProductModel)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type')
    list_filter = ('product_type',)
    search_fields = ('name',)
class CustomProductAdmin(admin.ModelAdmin):
    list_display = ('serial_number', 'model', 'created_at')
    exclude = ('serial_number', 'qr_code')
    change_list_template = "admin/guide/product/change_list.html"
    actions = ['export_qr_pdf']
    def export_qr_pdf(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "Выберите хотя бы один товар.", level='error')
            return

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="qr_codes_{timezone.now().date()}.pdf"'

        p = canvas.Canvas(response, pagesize=A4)
        width, height = A4
        x, y = 20 * mm, height - 30 * mm

        for product in queryset:
            p.setFont("Helvetica", 10)
            p.drawString(x, y, f"{product.serial_number}")

            if product.qr_code and product.qr_code.path:
                try:
                    p.drawImage(product.qr_code.path, x + 150, y - 18, width=40 * mm, height=40 * mm)
                except Exception:
                    p.drawString(x, y - 10, "QR-код не найден")

            y -= 50 * mm
            if y < 50 * mm:
                p.showPage()
                y = height - 30 * mm

        p.save()
        return response

    export_qr_pdf.short_description = "Скачать PDF с QR-кодами"

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('generate/', self.admin_site.admin_view(self.generate_products_view), name='generate-products')
        ]
        return custom_urls + urls

    def generate_products_view(self, request):
        from django.shortcuts import render, redirect
        from .forms import GenerateBulkProductsForm
        from django.utils import timezone
        import qrcode
        from io import BytesIO
        from django.core.files import File
        from .models import Product

        if request.method == 'POST':
            form = GenerateBulkProductsForm(request.POST)
            if form.is_valid():
                model = form.cleaned_data['model']
                quantity = form.cleaned_data['quantity']

                for i in range(quantity):
                    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
                    serial_number = f"{model.name[:3].upper()}-{timestamp}-{i:03d}"
                    product = Product.objects.create(model=model, serial_number=serial_number)

                    qr_url = f"http://127.0.0.1:8000{product.get_absolute_url()}"
                    qr = qrcode.make(qr_url)
                    buffer = BytesIO()
                    qr.save(buffer)
                    product.qr_code.save(f"qr_{serial_number}.png", File(buffer), save=True)

                self.message_user(request, f"Создано {quantity} товаров", level=messages.SUCCESS)
                return redirect('..')
        else:
            form = GenerateBulkProductsForm()

        return render(request, 'admin/guide/product/generate_products.html', {'form': form})

admin.site.register(Product, CustomProductAdmin)



@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = ('product', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__serial_number',)

class MovementForm(forms.Form):
    products = forms.ModelMultipleChoiceField(
        queryset=Product.objects.all(),
        label="Выберите товары",
        widget=forms.SelectMultiple(attrs={'size': '10'})
    )
    move_type = forms.ChoiceField(choices=Movement.MOVE_TYPES, label="Тип перемещения")
    location = forms.CharField(max_length=100, label="Местоположение")

@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ('product', 'get_move_type_display', 'location', 'date')
    list_filter = ('move_type', 'date')
    search_fields = ('product__serial_number', 'location')
    change_list_template = "admin/guide/movement/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate/', self.admin_site.admin_view(self.bulk_create_view), name='generate-movements')
        ]
        return custom_urls + urls

    def bulk_create_view(self, request):
        if request.method == 'POST':
            form = MovementForm(request.POST)
            if form.is_valid():
                products = form.cleaned_data['products']
                move_type = form.cleaned_data['move_type']
                location = form.cleaned_data['location']

                for product in products:
                    Movement.objects.create(
                        product=product,
                        move_type=move_type,
                        location=location
                    )

                self.message_user(request, f"Создано {products.count()} перемещений.", level=messages.SUCCESS)
                return redirect("..")
        else:
            form = MovementForm()

        return render(request, 'admin/guide/movement/generate_movements.html', {'form': form})

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'message')
    search_fields = ('name', 'email', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('name', 'email', 'message', 'created_at')
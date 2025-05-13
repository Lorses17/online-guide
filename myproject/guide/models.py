from django.db import models
from django.core.validators import FileExtensionValidator
import uuid

def generate_serial_number():
    return str(uuid.uuid4().hex[:12].upper())

class ProductType(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Тип техники")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тип техники"
        verbose_name_plural = "Тип техники"
class ProductModel(models.Model):
    product_type = models.ForeignKey(
        'ProductType',
        on_delete=models.CASCADE,
        related_name='models',
        verbose_name="Тип техники"
    )
    name = models.CharField(max_length=100, verbose_name="Модель")

    def __str__(self):
        return f"{self.product_type.name}, модель {self.name}"

    class Meta:
        verbose_name = "Модель техники"
        verbose_name_plural = "Модели техники"
class Product(models.Model):
    serial_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Серийный номер"
    )
    model = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="Модель"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        verbose_name="QR-код",
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])]
    )

    def __str__(self):
        return f"{self.model.name} ({self.serial_number})"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('search_product') + f"?serial_number={self.serial_number}"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

class Warranty(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='warranty',
        verbose_name="Товар"
    )
    start_date = models.DateField(verbose_name="Дата начала гарантии")
    end_date = models.DateField(verbose_name="Дата окончания гарантии")
    terms = models.TextField(verbose_name="Условия гарантии")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def __str__(self):
        return f"Гарантия для {self.product.model.name} ({self.start_date} - {self.end_date})"

    class Meta:
        verbose_name = "Гарантия"
        verbose_name_plural = "Гарантии"
class Movement(models.Model):
    MOVE_TYPES = [
        ('in', 'Поступление на склад'),
        ('out', 'Поставлен в магазин'),
        ('repair', 'В ремонте'),
        ('in_use', 'В использовании'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name="Товар"
    )
    move_type = models.CharField(
        max_length=20,
        choices=MOVE_TYPES,
        verbose_name="Тип перемещения"
    )
    location = models.CharField(max_length=100, verbose_name="Местоположение")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата перемещения")

    def __str__(self):
        return f"{self.get_move_type_display()} в {self.location} ({self.date})"

    class Meta:
        verbose_name = "Перемещение"
        verbose_name_plural = "Перемещения"
class Feedback(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")

    def __str__(self):
        return f"{self.email} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        verbose_name = "Обращение"
        verbose_name_plural = "Обращения"
        ordering = ['-created_at']


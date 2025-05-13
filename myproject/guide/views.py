from django.shortcuts import render, redirect
from .forms import SearchForm, FeedbackForm, ProductTypeForm, ProductModelForm
from .models import Product,Feedback
from django.core.mail import EmailMessage, get_connection

def search_product(request):
    form = SearchForm(request.GET or None)
    product = None
    not_found = False

    if form.is_valid():
        serial = form.cleaned_data['serial_number']
        try:
            product = Product.objects.get(serial_number=serial)
        except Product.DoesNotExist:
            not_found = True

    return render(request, 'search.html', {
        'form': form,
        'product': product,
        'not_found': not_found
    })

def send_feedback_email(feedback):
    try:
        connection = get_connection()
        connection.local_hostname = 'localhost'
        connection.open()

        email = EmailMessage(
            subject='Новое сообщение с сайта',
            body=(
                f"Имя: {feedback.name}\n"
                f"Email: {feedback.email}\n\n"
                f"Сообщение:\n{feedback.message}"
            ),
            from_email='techcompany32@yandex.ru',
            to=['techcompany32@yandex.ru'],
            reply_to=[feedback.email],
            connection=connection
        )
        email.send()
        connection.close()
    except Exception as e:
        print("Ошибка при отправке письма:", e)

def contact(request):
    success = False
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()
            send_feedback_email(feedback)
            success = True
    else:
        form = FeedbackForm()

    return render(request, 'contact.html', {'form': form, 'success': success})


def add_product_type(request):
    if request.method == 'POST':
        form = ProductTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductTypeForm()
    return render(request, 'add_product_type.html', {'form': form})

def add_product_model(request):
    if request.method == 'POST':
        form = ProductModelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductModelForm()
    return render(request, 'add_product_model.html', {'form': form})

def home(request):
    return render(request, 'home.html')

def services(request):
    return render(request, 'services.html')

def about(request):
    return render(request, 'about.html')

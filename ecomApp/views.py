from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import Profile, Product, SearchLog  # Import the Profile model here
from .forms import WholesellerForm, CustomerForm, ProductForm
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

def register_view(request):
    role = request.GET.get('role', 'Wholeseller')  # Default to Wholeseller

    if request.method == 'POST':
        if role == 'Wholeseller':
            form = WholesellerForm(request.POST)
            if form.is_valid():
                # Check if username already exists
                username = form.cleaned_data['name']
                if User.objects.filter(username=username).exists():
                    form.add_error('name', 'Username already exists. Please choose a different one.')
                else:
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=form.cleaned_data['email'],
                            password=form.cleaned_data['password']
                        )

                        # Create the Profile after the user is created
                        user.profile = Profile.objects.create(
                            user=user,
                            role='Wholeseller',
                            company_name=form.cleaned_data['company_name'],
                            address=form.cleaned_data['address']
                        )
                        return redirect('success_page')  # Redirect to a success page
                    except IntegrityError:
                        form.add_error('name', 'Username already exists. Please choose a different one.')

        elif role == 'Customer':
            form = CustomerForm(request.POST)
            if form.is_valid():
                # Check if username already exists
                username = form.cleaned_data['name']
                if User.objects.filter(username=username).exists():
                    form.add_error('name', 'Username already exists. Please choose a different one.')
                else:
                    try:
                        user = User.objects.create_user(
                            username=username,
                            email=form.cleaned_data['email'],
                            password=form.cleaned_data['password']
                        )

                        # Create the Profile for the user
                        user.profile = Profile.objects.create(
                            user=user,
                            role='Customer',
                            sell_on_amazon=form.cleaned_data['sell_on_amazon'],
                            sell_on_flipkart=form.cleaned_data['sell_on_flipkart'],
                            sell_on_meesho=form.cleaned_data['sell_on_meesho']
                        )
                        return redirect('success_page')  # Redirect to a success page
                    except IntegrityError:
                        form.add_error('name', 'Username already exists. Please choose a different one.')

    else:
        form = WholesellerForm() if role == 'Wholeseller' else CustomerForm()

    return render(request, 'ecomApp/register.html', {'form': form, 'role': role})


def login_view(request):
    next_url = request.GET.get('next', 'homepage')  # Default to 'homepage' if 'next' is not provided
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'ecomApp/login.html', {'next': next_url, 'error_message': 'Invalid username or password.'})
    return render(request, 'ecomApp/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    return redirect('login')

def homepage_view(request):
    return render(request, 'ecomApp/homepage.html')


from django.db.models import Q
from django.core.paginator import Paginator
from rapidfuzz import process, fuzz

def search_view(request):
    query = request.GET.get('q', '')  # Retrieve search query
    category_id = request.GET.get('category', '')  # Retrieve category from URL parameters
    sort = request.GET.get('sort', '')
    page_number = request.GET.get('page', 1)  # Get the current page number

    products = Product.objects.filter(user__profile__role='Wholeseller')  # Base queryset

    # Apply sorting
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'below_99':
        products = products.filter(price__lt=99)
    elif sort == 'below_249':
        products = products.filter(price__lt=249)

    # Process the query and apply fuzzy matching
    if query:
        # Retrieve all product names and their IDs
        product_data = list(products.values('id', 'name'))
        product_names = [item['name'] for item in product_data]

        # Use fuzzy matching to find products that closely match the query
        matches = process.extract(query, product_names, scorer=fuzz.partial_ratio, limit=10)

        # If any matches found, filter products based on matched IDs
        matched_ids = [
            product_data[i]['id'] for match, score, i in matches if score >= 60  # Adjust score threshold
        ]

        # Ensure the query results include products with a matching name
        if matched_ids:
            products = products.filter(id__in=matched_ids)

    # Filter by category if selected
    if category_id:
        products = products.filter(category=category_id)

    # Paginate the products queryset
    paginator = Paginator(products, 8)  # 8 products per page
    paginated_products = paginator.get_page(page_number)

    # Fetch categories from the product table
    categories = Product.objects.values_list('category', flat=True).distinct()

    return render(request, 'ecomApp/search.html', {
        'products': paginated_products,
        'query': query,
        'categories': categories,
        'selected_category': category_id,
        'sort': sort,
    })



@login_required
def products_view(request):
    # Retrieve all products
    products = Product.objects.filter(user=request.user)

    # Pagination logic
    page_number = request.GET.get('page', 1)  # Get the page number from the query parameters
    paginator = Paginator(products, 8)  # 8 products per page (you can change this number)
    paginated_products = paginator.get_page(page_number)  # Get the products for the current page

    # Render the page with the paginated products
    return render(request, 'ecomApp/products.html', {'products': paginated_products})


@login_required
def addproduct_view(request):
    if request.method == 'POST':
        # Get form data
        product_name = request.POST.get('product_name')
        sku = request.POST.get('sku')
        price = request.POST.get('price')
        hsn_code = request.POST.get('hsn_code')
        carton_quantity = request.POST.get('pieces_per_carton')
        in_stock = request.POST.get('in_stock') == 'true'
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Optional: Validate the data (e.g., check for unique SKU)
        if Product.objects.filter(sku=sku).exists():
            return HttpResponse("A product with this SKU already exists!")

        # Save the product
        Product.objects.create(
            name=product_name,
            sku=sku,
            price=price,
            hsn_code=hsn_code,
            carton_quantity=carton_quantity,
            in_stock=in_stock,
            category=category,
            image=image,
            user=request.user,
        )
        # Add success message
        messages.success(request, "Product added successfully!")

        return redirect('products')  # Replace 'success_page' with your URL name

    context = {'category_choices': Product.CATEGORY_CHOICES}

    return render(request, 'ecomApp/addproducts.html', context)  # Ensure this template exists


@login_required
def editproduct_view(request, id):
    # Fetch product by ID
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        # Initialize the form with POST and FILES data
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()  # Save the updated product
            messages.success(request, 'Product updated successfully!')
            return redirect('products')  # Redirect to the products list
        else:
            # In case of form errors, display them in the template
            messages.error(request, 'Please correct the errors below.')
    else:
        # Initialize form with the current product instance for GET request
        form = ProductForm(instance=product)

    # Debug: Check form instance ID (can be removed in production)
    print(f"Form instance ID: {form.instance.id}")

    return render(request, 'ecomApp/editproduct.html', {'form': form})


def deleteproduct_view(request, id):
    if request.method == 'POST':
        # Get the product object by ID
        product = get_object_or_404(Product, id=id)

        # Delete the product
        product.delete()

        # Optionally, add a success message
        messages.success(request, "Product deleted successfully.")

        # Redirect back to the product list
        return redirect('products')
    else:
        # If not a POST request, redirect to the product list
        return redirect('products')

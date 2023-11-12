from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .models import *
from .utils import cookieCart, cartData

# Create your views here.
def store(request):
    data = cartData(request)
    cartItems = data['cartItems']
    
    
    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'store.html', context)

def cart(request):
    
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
                
    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'cart.html',context)


def checkout(request):
     
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'checkout.html', context)

def settings(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer= customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False }
        cartItems = order['get_cart_items']
    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render (request, 'settings.html', context)
def login(request):
    return render (request,'index.html')
def About(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer= customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False }
        cartItems = order['get_cart_items']
    context={'items':items, 'order':order, 'cartItems':cartItems}
    return render (request,'About.html',context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    
    print('Action:',action)
    print('productId:', productId)
    
    customer= request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer= customer, complete=False)
    
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product )
    
    if action =='add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action =='remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()
    if orderItem.quantity <= 0 :
        orderItem.delete()
    return JsonResponse('Item was added', safe=False) 


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer= customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id
        
        if total == order.get_cart_total:
            order.complete = True
        order.save()
        
        if order.shipping == True:
            ShippingAddress.objects.create(
                Customer = customer,
                Order = order,
                Address= data['shipping']['address'],
                City= data['shipping']['city'],
                State= data['shipping']['state'],
                Zipcode= data['shipping']['zipcode'],
            )
        
    else:
        print('User is not logged in..')
    return JsonResponse('Payment complete', safe=False) 
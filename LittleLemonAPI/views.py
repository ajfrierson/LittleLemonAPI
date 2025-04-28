from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework import viewsets 
from rest_framework import generics, status
from .models import MenuItem
from .serializers import MenuItemSerializer
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .throttles import TenCallsPerMinute
from django.contrib.auth.models import User, Group


# Create your views here.
# class MenuItemsView(generics.ListCreateAPIView):
#     queryset = MenuItems.objects.all()
#     serializer_class = MenuItemSerializer

# class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
#     queryset = MenuItems.objects.all()
#     serializer_class = MenuItemSerializer

'''
Class based paginations
    '''
# class MenuItemsViewSet(viewsets.ModelViewSet):
#     queryset = MenuItems.objects.all()
#     serializer_class = MenuItemSerializer
#     ordering_fields = ['price', 'inventory']
#     search_fields = ['title', 'category__title']

'''
Function based search, filtering and pagination
'''    
@api_view(['GET', 'POST'])    
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage', default=2)
        page = request.query_params.get('page', default=1)
        if category_name:
            items = items.filter(category__title=category_name)
            # price__lte means filter for a price less than or equal to "price__lte=to_price"
        if to_price:
            items = items.filter(price=to_price)
        if search:
            items = items.filter(title__istartswith=search)
        if ordering:
            # items = items.order_by(ordering)
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many=True)
        return Response(serialized_item.data)
    if request.method == 'POST':
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
def single_item(request, id):
     if request.method == 'DELETE':
        item = get_object_or_404(MenuItem, pk=id)
        item.delete()
        return Response('Item has been deleted!', status.HTTP_200_OK)
     else:
        item = get_object_or_404(MenuItem, pk=id)
        serialized_item = MenuItemSerializer(item)
        return Response(serialized_item.data)

   
@api_view()
@permission_classes([IsAuthenticated])
def secret(request):
    return Response({'message': 'Some secret message'})


@api_view()
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({'message': 'Only Manager Should See This'})
    else:
        return Response({'message': 'You are not authorized'}, status.HTTP_403_FORBIDDEN)
    
@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({'message': 'successful'})


@api_view()
@throttle_classes([TenCallsPerMinute])
@permission_classes([IsAuthenticated])
def throttle_check_auth(request):
    return Response({'message': 'message for the logged in users only'})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='Manager')
        if request.method == 'POST':
            managers.user_set.add(user)
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
        return Response({'message': 'ok'})
    
    return Response({'message': 'error'}, status.HTTP_400_BAD_REQUEST)
from decimal import Decimal
from rest_framework import serializers # type: ignore
from .models import MenuItem, Category
from rest_framework.validators import UniqueValidator
import bleach


class CategorySerializer (serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(max_digits=6, decimal_places=2)
    unit_price = serializers.SerializerMethodField(method_name='unit_price')
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=2)
    # def validate_title(self, attrs):
    #     attrs['title'] = bleach.clean(attrs['title'])
    #     return super().validate(attrs)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'unit_price', 'category', 'category_id']
        extra_kwargs = {
            'price': {'min_value': 2},
            'quantity':{'source':'quantity', 'min_value': 0},
            'title': {
                'validators': [
                    UniqueValidator(
                        queryset=MenuItem.objects.all()
                    )
                ]
            }
        }
    def calculate_tax(self, product:MenuItem):
        return product.price * Decimal(1.1)


# regular serializer used to convert model data to JSON data
# class MenuItemSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
#     price = serializers.DecimalField(max_digits=6, decimal_places=2)
#     inventory = serializers.IntegerField()
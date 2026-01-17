import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        filter_fields = {}
        interfaces = (graphene.relay.Node,)
        fields = '__all__'


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        filter_fields = {}
        interfaces = (graphene.relay.Node,)
        fields = '__all__'


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        filter_fields = {}
        interfaces = (graphene.relay.Node,)
        fields = '__all__'


class Query(graphene.ObjectType):
    hello = graphene.String(description="A simple hello query")
    
    # Filtered queries using DjangoFilterConnectionField
    all_customers = DjangoFilterConnectionField(
        CustomerType,
        filterset_class=CustomerFilter
    )
    all_products = DjangoFilterConnectionField(
        ProductType,
        filterset_class=ProductFilter
    )
    all_orders = DjangoFilterConnectionField(
        OrderType,
        filterset_class=OrderFilter
    )

    def resolve_hello(self, info):
        return "Hello, GraphQL!"


schema = graphene.Schema(query=Query)

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CheckoutResolverView, PagoViewSet

app_name = "pagos"

router = DefaultRouter()
router.register("pagos", PagoViewSet, basename="pago")

urlpatterns = [
    # Antes del router: "checkout" no debe interpretarse como un {pk}.
    path(
        "pagos/checkout/resolver/",
        CheckoutResolverView.as_view(),
        name="checkout-resolver",
    ),
    *router.urls,
]

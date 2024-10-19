from django.http import JsonResponse

from .models import Stock


def search_stocks(request):
    query = request.GET.get("q", "")

    if query:
        results = Stock.objects.filter(name__icontains=query)
        data = [
            {"id": stock.id, "name": stock.name, "current_price": stock.current_price}
            for stock in results
        ]
    else:
        data = []

    return JsonResponse(data, safe=False)

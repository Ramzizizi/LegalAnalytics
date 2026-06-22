def basket_count(request):
    if request.user.is_authenticated:
        basket = request.session.get('basket', {'norms': [], 'cases': []})
        return {'basket_count': len(basket.get('norms', [])) + len(basket.get('cases', []))}
    return {'basket_count': 0}

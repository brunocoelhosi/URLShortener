from ninja import Router

shortener_router = Router()

@shortener_router.get('create/')
def create(request):
    return {'status':'OK'}
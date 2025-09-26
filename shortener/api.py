from ninja import Router
from .schemas import LinkSchema, UpdateLinkSchema
from .models import Links, Clicks
from django.shortcuts import get_object_or_404,redirect
import qrcode

shortener_router = Router()

@shortener_router.post('create/', response = {200: LinkSchema, 409: dict})
def create(request, link_schema: LinkSchema):
    print(link_schema.to_model_data())
    data = link_schema.to_model_data()

    token = data['token']

    if token and Links.objects.filter(token=token).exists():
        return 409, {'error':'Token already exists'}
    
    link = Links(**data)
    link.save()
    
    return 200, LinkSchema.from_model(link)

@shortener_router.get('/{token}', response={200: dict, 404: dict})
def redirect_link(request, token):
    link = get_object_or_404(Links, token=token, active=True)

    if link.expired():
        return 404, {'error': 'Link expired'}
    

    unique_clicks = Clicks.objects.filter(link=link).values('ip').distinct().count()

    if link.max_unique_cliques and unique_clicks >= link.max_unique_cliques:
        return 404, {'error': 'Link expired'}
    
    click = Clicks(
        link=link,
        ip=request.META['REMOTE_ADDR'], #ip do usuario que clicou no link
    )

    click.save()

    return redirect(link.redirect_link)


@shortener_router.put('/{link_id}/', response={200: UpdateLinkSchema, 409: dict})
def update_link(request, link_id: int, link_schema: UpdateLinkSchema):
    link = get_object_or_404(Links, id=link_id)
    data = link_schema.dict()

    token = data['token']

    if token and Links.objects.filter(token=token).exclude(id=link_id).exists():
        return 409, {'error':'Token already exists'}

    for field, value in data.items():
        if value:
            setattr(link, field, value)

    link.save()

    return 200, LinkSchema.from_model(link)

@shortener_router.get('/', response={200: list[LinkSchema], 404: dict})
def list_links(request):
    links = Links.objects.all()
    if not links.exists():
        return 404, {"detail": "Nenhum link encontrado"}
    
    response = [LinkSchema.from_model(link) for link in links]
    return 200, response
    
@shortener_router.get('statistics/{link_id}', response={200: dict, 404: dict})
def statistics(request, link_id: int):
    link = get_object_or_404(Links, id=link_id)
    total_clicks = Clicks.objects.filter(link=link).count()
    unique_clicks = Clicks.objects.filter(link=link).values('ip').distinct().count()

    return 200, {"unique_clicks": unique_clicks, "total_clicks": total_clicks}
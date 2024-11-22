from ninja import NinjaAPI

api = NinjaAPI()
api.add_router("/currency/", "currencies.api.router")

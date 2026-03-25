from slowapi.util import get_remote_address


def user_key(request):
    if request.state.user:  # depends on your auth setup
        return str(request.state.user.id)
    return get_remote_address(request)


def api_key_key(request):
    return request.headers.get("X-API-Key", "anonymous")


def real_ip(request):
    return request.headers.get("X-Forwarded-For", request.client.host)

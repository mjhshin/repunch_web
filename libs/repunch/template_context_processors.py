from parse import session as SESSION


def active_store_location(request):
    ses = request.session
    return { "active_store_location": SESSION.get_store_location(ses,
        SESSION.get_active_store_location_id(ses)) }

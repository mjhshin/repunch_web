from parse import session as SESSION


def active_store_location(request):
    """
    Inserts the active_store_location object in the context.
    """
    if "account" not in request.session:
        return {}
        
    ses = request.session
    return { "active_store_location": SESSION.get_store_location(ses,
        SESSION.get_active_store_location_id(ses)) }
        
def store_locations(request):
    """
    Inserts the ordered list (by createdAt) of store_locations.
    """
    if "account" not in request.session:
        return {}
        
    # use sorted locations by createdAt
    store_locations = [ v for v in SESSION.get_store_locations(\
        request.session).values() ]
    store_locations.sort(key=lambda l: l.createdAt) 
    
    return { 'store_locations': store_locations }

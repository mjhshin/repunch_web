"""
Tutorials views.
"""

from parse.auth.decorators import dev_login_required

@dev_login_required
def index(request):
    """
    The tutorials index page.
    """
    pass
    
    

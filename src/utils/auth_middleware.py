from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(f):
    """
    Decorator to ensure that a user is logged in before accessing a route.
    If not logged in, redirects to the login page.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # Store the requested URL for redirecting after login
            session['next_url'] = request.url
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator to ensure that a user is an admin before accessing a route.
    If not an admin, redirects to the home page with an error message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('is_admin', False) != True:
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('web.index'))
        return f(*args, **kwargs)
    return decorated_function 
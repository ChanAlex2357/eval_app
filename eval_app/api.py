import frappe
from frappe import _
import traceback

class ApiResponse:
    def __init__(self, success=True, message="", data=None, errors=None):
        self.success = bool(success)
        self.message = message or _("No message")
        self.data = data or {}
        self.errors = errors or []

    def as_dict(self):
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "errors": self.errors,
        }

def make_response(success=True, message="", data=None, errors=None):
    return ApiResponse(success=success, message=message, data=data, errors=errors).as_dict()


@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError as e:
        frappe.clear_messages()
        frappe.log_error(
            title="Authentication Failed",
            message=traceback.format_exc()
        )
        return make_response(
            success=False,
            message=traceback.format_exc(),
        )
    except Exception as e:
        # Catch any unexpected errors
        frappe.log_error(
            title="Login Error",
            message=traceback.format_exc()
        )
        return make_response(
            success=False,
            message="An unexpected error occurred. Please try again later.",
        )

    api_secret = generate_keys(frappe.session.user)
    user = frappe.get_doc('User', frappe.session.user)

    return make_response(
        success=True,
        message="Authentication success",
        data={
            "sid": frappe.session.sid,
            "api_key": user.api_key,
            "api_secret": api_secret,
            "username": user.username,
            "full_name":user.full_name,
            "email": user.email
        }
    )

def generate_keys(user):
    user_details = frappe.get_doc('User', user)
    api_secret = frappe.generate_hash(length=15)

    if not user_details.api_key:
        api_key = frappe.generate_hash(length=15)
        user_details.api_key = api_key

    user_details.api_secret = api_secret
    user_details.save()

    return api_secret
from django.contrib.auth import get_user

class ProfileGetObjectMixin:
	def get_object(self, queryset=None):
		current_user = get_user(self.request)
		return current_user.profile
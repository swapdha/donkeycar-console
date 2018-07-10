from django.contrib import admin
from .models import Jobs
from .models import credentials
from .models import remarks
from .models import github
from .models import controller
from .models import local_directory


# Register your models here.
admin.site.register(remarks)
admin.site.register(Jobs)
admin.site.register(credentials)
admin.site.register(github)
admin.site.register(controller)
admin.site.register(local_directory)
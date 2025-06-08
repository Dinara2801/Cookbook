from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import User, Follow


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name',
                       'last_name', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'avatar', 'image_preview',
                    'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('last_login', 'image_preview')

    def image_preview(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="180" height="160">'
            )
        return 'Изображение отсутствует'

    image_preview.short_description = 'Просмотр изображения'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_username', 'following_username')
    search_fields = ('user__username', 'following__username')

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'User'

    def following_username(self, obj):
        return obj.following.username
    following_username.short_description = 'Following'

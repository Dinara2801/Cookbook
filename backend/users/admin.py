from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import Follow, User


@admin.register(User)
class UserAdminConfig(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser',
                       'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name',
                       'last_name', 'password1', 'password2'),
        }),
    )
    list_display = (
        'username', 'email', 'avatar', 'image_preview',
        'first_name', 'last_name', 'is_staff', 'is_active',
        'recipes_count', 'subscribers_count',
    )
    search_fields = ('username', 'email')
    ordering = ('username',)
    readonly_fields = ('last_login', 'image_preview')

    @admin.display(description='Просмотр изображения')
    def image_preview(self, obj):
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" width="180" height="160">'
            )
        return 'Изображение отсутствует'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(
            _recipes_count=Count('recipes', distinct=True),
            _subscribers_count=Count('subscribers', distinct=True),
        )

    @admin.display(description='Количество рецептов')
    def recipes_count(self, obj):
        return getattr(obj, '_recipes_count', 0)

    @admin.display(description='Количество подписчиков')
    def subscribers_count(self, obj):
        return getattr(obj, '_subscribers_count', 0)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_username', 'author_username')
    search_fields = ('user__username', 'author__username')

    @admin.display(description='Пользователь')
    def user_username(self, obj):
        return obj.user.username

    @admin.display(description='Автор')
    def author_username(self, obj):
        return obj.author.username

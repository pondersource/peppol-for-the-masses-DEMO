from __future__ import absolute_import

from django.contrib import admin

from .models import Block, Follow, Contact, ConnectionRequest


class BlockAdmin(admin.ModelAdmin):
    model = Block
    raw_id_fields = ("blocker", "blocked")


class FollowAdmin(admin.ModelAdmin):
    model = Follow
    raw_id_fields = ("follower", "followee")


class ContactAdmin(admin.ModelAdmin):
    model = Contact
    raw_id_fields = ("to_user", "from_user")


class ConnectionRequestAdmin(admin.ModelAdmin):
    model = ConnectionRequest
    raw_id_fields = ("from_user", "to_user")


admin.site.register(Block, BlockAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ConnectionRequest, ConnectionRequestAdmin)

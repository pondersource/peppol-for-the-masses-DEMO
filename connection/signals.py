from django.dispatch import Signal

connection_request_created = Signal()
connection_request_rejected = Signal()
connection_request_canceled = Signal()
connection_request_viewed = Signal()
connection_request_accepted = Signal()
connection_removed = Signal()
follower_created = Signal()
follower_removed = Signal()
followee_created = Signal()
followee_removed = Signal()
following_created = Signal()
following_removed = Signal()
block_created = Signal()
block_removed = Signal()

import os

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse

from connection.exceptions import AlreadyExistsError, AlreadyFriendsError
from connection.models import Block, Follow, Friend, FriendshipRequest

TEST_TEMPLATES = os.path.join(os.path.dirname(__file__), "templates")


class login(object):
    def __init__(self, testcase, user, password):
        self.testcase = testcase
        success = testcase.client.login(username=user, password=password)
        self.testcase.assertTrue(
            success, "login with username=%r, password=%r failed" % (user, password)
        )

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.testcase.client.logout()


class BaseTestCase(TestCase):
    def setUp(self):
        """
        Setup some initial users

        """
        self.user_pw = "test"
        self.user_bob = self.create_user("bob", "bob@bob.com", self.user_pw)
        self.user_steve = self.create_user("steve", "steve@steve.com", self.user_pw)
        self.user_susan = self.create_user("susan", "susan@susan.com", self.user_pw)
        self.user_amy = self.create_user("amy", "amy@amy.amy.com", self.user_pw)
        cache.clear()

    def tearDown(self):
        cache.clear()
        self.client.logout()

    def login(self, user, password):
        return login(self, user, password)

    def create_user(self, username, email_address, password):
        user = User.objects.create_user(username, email_address, password)
        return user

    def assertResponse200(self, response):
        self.assertEqual(response.status_code, 200)

    def assertResponse302(self, response):
        self.assertEqual(response.status_code, 302)

    def assertResponse403(self, response):
        self.assertEqual(response.status_code, 403)

    def assertResponse404(self, response):
        self.assertEqual(response.status_code, 404)


class FriendshipModelTests(BaseTestCase):
    def test_connection_request(self):
        # Bob wants to be connections with Steve
        req1 = Friend.objects.add_connection(self.user_bob, self.user_steve)

        # Ensure neither have connections already
        self.assertEqual(Friend.objects.connections(self.user_bob), [])
        self.assertEqual(Friend.objects.connections(self.user_steve), [])

        # Ensure FriendshipRequest is created
        self.assertEqual(
            FriendshipRequest.objects.filter(from_user=self.user_bob).count(), 1
        )
        self.assertEqual(
            FriendshipRequest.objects.filter(to_user=self.user_steve).count(), 1
        )
        self.assertEqual(Friend.objects.unread_request_count(self.user_steve), 1)

        # Ensure the proper sides have requests or not
        self.assertEqual(len(Friend.objects.requests(self.user_bob)), 0)
        self.assertEqual(len(Friend.objects.requests(self.user_steve)), 1)
        self.assertEqual(len(Friend.objects.sent_requests(self.user_bob)), 1)
        self.assertEqual(len(Friend.objects.sent_requests(self.user_steve)), 0)

        self.assertEqual(len(Friend.objects.unread_requests(self.user_steve)), 1)
        self.assertEqual(Friend.objects.unread_request_count(self.user_steve), 1)

        self.assertEqual(len(Friend.objects.rejected_requests(self.user_steve)), 0)

        self.assertEqual(len(Friend.objects.unrejected_requests(self.user_steve)), 1)
        self.assertEqual(Friend.objects.unrejected_request_count(self.user_steve), 1)

        # Ensure they aren't connections at this point
        self.assertFalse(Friend.objects.are_connections(self.user_bob, self.user_steve))

        # Ensure Bob can't request another connection request from Steve.
        with self.assertRaises(AlreadyExistsError):
            Friend.objects.add_connection(self.user_bob, self.user_steve)

        # Ensure Steve can't request a connection request from Bob.
        with self.assertRaises(AlreadyExistsError):
            Friend.objects.add_connection(self.user_steve, self.user_bob)

        # Accept the request
        req1.accept()

        # Ensure neither have pending requests
        self.assertEqual(
            FriendshipRequest.objects.filter(from_user=self.user_bob).count(), 0
        )
        self.assertEqual(
            FriendshipRequest.objects.filter(to_user=self.user_steve).count(), 0
        )

        # Ensure both are in each other's connection lists
        self.assertEqual(Friend.objects.connections(self.user_bob), [self.user_steve])
        self.assertEqual(Friend.objects.connections(self.user_steve), [self.user_bob])
        self.assertTrue(Friend.objects.are_connections(self.user_bob, self.user_steve))

        # Make sure we can remove connection
        self.assertTrue(Friend.objects.remove_connection(self.user_bob, self.user_steve))
        self.assertFalse(Friend.objects.are_connections(self.user_bob, self.user_steve))
        self.assertFalse(Friend.objects.remove_connection(self.user_bob, self.user_steve))

        # Susan wants to be connections with Amy, but cancels it
        req2 = Friend.objects.add_connection(self.user_susan, self.user_amy)
        self.assertEqual(Friend.objects.connections(self.user_susan), [])
        self.assertEqual(Friend.objects.connections(self.user_amy), [])
        req2.cancel()
        self.assertEqual(Friend.objects.requests(self.user_susan), [])
        self.assertEqual(Friend.objects.requests(self.user_amy), [])

        # Susan wants to be connections with Amy, but Amy rejects it
        req3 = Friend.objects.add_connection(self.user_susan, self.user_amy)
        self.assertEqual(Friend.objects.connections(self.user_susan), [])
        self.assertEqual(Friend.objects.connections(self.user_amy), [])
        req3.reject()

        # Duplicated requests raise a more specific subclass of IntegrityError.
        with self.assertRaises(AlreadyExistsError):
            Friend.objects.add_connection(self.user_susan, self.user_amy)

        self.assertFalse(Friend.objects.are_connections(self.user_susan, self.user_amy))
        self.assertEqual(len(Friend.objects.rejected_requests(self.user_amy)), 1)
        self.assertEqual(len(Friend.objects.rejected_requests(self.user_amy)), 1)

        # let's try that again..
        req3.delete()

        # Susan wants to be connections with Amy, and Amy reads it
        req4 = Friend.objects.add_connection(self.user_susan, self.user_amy)
        req4.mark_viewed()

        self.assertFalse(Friend.objects.are_connections(self.user_susan, self.user_amy))
        self.assertEqual(len(Friend.objects.read_requests(self.user_amy)), 1)

        # Ensure we can't be connections with ourselves
        with self.assertRaises(ValidationError):
            Friend.objects.add_connection(self.user_bob, self.user_bob)

        # Ensure we can't do it manually either
        with self.assertRaises(ValidationError):
            Friend.objects.create(to_user=self.user_bob, from_user=self.user_bob)

    def test_already_connections_with_request(self):
        # Make Bob and Steve connections
        req = Friend.objects.add_connection(self.user_bob, self.user_steve)
        req.accept()

        with self.assertRaises(AlreadyFriendsError):
            Friend.objects.add_connection(self.user_bob, self.user_steve)

        with self.assertRaises(AlreadyFriendsError):
            Friend.objects.add_connection(self.user_steve, self.user_bob)

    def test_multiple_connection_requests(self):
        """ Ensure multiple connection requests are handled properly """
        # Bob wants to be connections with Steve
        req1 = Friend.objects.add_connection(self.user_bob, self.user_steve)

        # Ensure neither have connections already
        self.assertEqual(Friend.objects.connections(self.user_bob), [])
        self.assertEqual(Friend.objects.connections(self.user_steve), [])

        # Ensure FriendshipRequest is created
        self.assertEqual(
            FriendshipRequest.objects.filter(from_user=self.user_bob).count(), 1
        )
        self.assertEqual(
            FriendshipRequest.objects.filter(to_user=self.user_steve).count(), 1
        )
        self.assertEqual(Friend.objects.unread_request_count(self.user_steve), 1)

        # Steve also wants to be connections with Bob before Bob replies
        with self.assertRaises(AlreadyExistsError):
            Friend.objects.add_connection(self.user_steve, self.user_bob)

        # Ensure they aren't connections at this point
        self.assertFalse(Friend.objects.are_connections(self.user_bob, self.user_steve))

        # Accept the request
        req1.accept()

        # Ensure neither have pending requests
        self.assertEqual(
            FriendshipRequest.objects.filter(from_user=self.user_bob).count(), 0
        )
        self.assertEqual(
            FriendshipRequest.objects.filter(to_user=self.user_steve).count(), 0
        )
        self.assertEqual(
            FriendshipRequest.objects.filter(from_user=self.user_steve).count(), 0
        )
        self.assertEqual(
            FriendshipRequest.objects.filter(to_user=self.user_bob).count(), 0
        )

    def test_multiple_calls_add_connection(self):
        """ Ensure multiple calls with same connections, but different message works as expected """
        Friend.objects.add_connection(self.user_bob, self.user_steve, message="Testing")

        with self.assertRaises(AlreadyExistsError):
            Friend.objects.add_connection(self.user_bob, self.user_steve, message="Foo Bar")

    def test_following(self):
        # Bob follows Steve
        Follow.objects.add_follower(self.user_bob, self.user_steve)
        self.assertEqual(len(Follow.objects.followers(self.user_steve)), 1)
        self.assertEqual(len(Follow.objects.following(self.user_bob)), 1)
        self.assertEqual(Follow.objects.followers(self.user_steve), [self.user_bob])
        self.assertEqual(Follow.objects.following(self.user_bob), [self.user_steve])

        self.assertTrue(Follow.objects.follows(self.user_bob, self.user_steve))
        self.assertFalse(Follow.objects.follows(self.user_steve, self.user_bob))

        # Duplicated requests raise a more specific subclass of IntegrityError.
        with self.assertRaises(IntegrityError):
            Follow.objects.add_follower(self.user_bob, self.user_steve)
        with self.assertRaises(AlreadyExistsError):
            Follow.objects.add_follower(self.user_bob, self.user_steve)

        # Remove the relationship
        self.assertTrue(Follow.objects.remove_follower(self.user_bob, self.user_steve))
        self.assertEqual(len(Follow.objects.followers(self.user_steve)), 0)
        self.assertEqual(len(Follow.objects.following(self.user_bob)), 0)
        self.assertFalse(Follow.objects.follows(self.user_bob, self.user_steve))

        # Ensure we canot follow ourselves
        with self.assertRaises(ValidationError):
            Follow.objects.add_follower(self.user_bob, self.user_bob)

        with self.assertRaises(ValidationError):
            Follow.objects.create(follower=self.user_bob, followee=self.user_bob)

    def test_blocking(self):
        # Bob blocks Steve
        Block.objects.add_block(self.user_bob, self.user_steve)
        self.assertEqual(len(Block.objects.blocking(self.user_bob)), 1)
        self.assertEqual(len(Block.objects.blocked(self.user_steve)), 1)
        self.assertEqual(Block.objects.is_blocked(self.user_bob, self.user_steve), True)

        # Duplicated requests raise a more specific subclass of IntegrityError.
        with self.assertRaises(IntegrityError):
            Block.objects.add_block(self.user_bob, self.user_steve)
        with self.assertRaises(AlreadyExistsError):
            Block.objects.add_block(self.user_bob, self.user_steve)

        # Remove the relationship
        self.assertTrue(Block.objects.remove_block(self.user_bob, self.user_steve))
        self.assertEqual(len(Block.objects.blocking(self.user_steve)), 0)
        self.assertEqual(len(Block.objects.blocked(self.user_bob)), 0)

        # Ensure we canot block ourselves
        with self.assertRaises(ValidationError):
            Block.objects.add_block(self.user_bob, self.user_bob)

        with self.assertRaises(ValidationError):
            Block.objects.create(blocker=self.user_bob, blocked=self.user_bob)


class FriendshipViewTests(BaseTestCase):
    def setUp(self):
        super(FriendshipViewTests, self).setUp()
        self.connection_request = Friend.objects.add_connection(
            self.user_steve, self.user_bob
        )

    def test_connection_view_users(self):
        url = reverse("connection_view_users")

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse200(response)

        with self.settings(
            CONNECTION_CONTEXT_OBJECT_LIST_NAME="object_list",
            TEMPLATE_DIRS=(TEST_TEMPLATES,),
        ):
            response = self.client.get(url)
            self.assertResponse200(response)
            self.assertTrue("object_list" in response.context)

    def test_connection_view_connections(self):
        url = reverse(
            "connection_view_connections", kwargs={"username": self.user_bob.username}
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse200(response)
        self.assertTrue("user" in response.context)

        with self.settings(
            CONNECTION_CONTEXT_OBJECT_NAME="object", TEMPLATE_DIRS=(TEST_TEMPLATES,)
        ):
            response = self.client.get(url)
            self.assertResponse200(response)
            self.assertTrue("object" in response.context)

    def test_connection_add_connection(self):
        url = reverse(
            "connection_add_connection", kwargs={"to_username": self.user_amy.username}
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            # if we don't POST the view should return the
            # connection_add_connection view
            response = self.client.get(url)
            self.assertResponse200(response)

            # on POST accept the connection request and redirect to the
            # connection_request_list view
            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse("connection_request_list")
            self.assertTrue(redirect_url in response["Location"])

    def test_connection_add_connection_dupe(self):
        url = reverse(
            "connection_add_connection", kwargs={"to_username": self.user_amy.username}
        )

        with self.login(self.user_bob.username, self.user_pw):
            # if we don't POST the view should return the
            # connection_add_connection view

            # on POST accept the connection request and redirect to the
            # connection_request_list view
            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse("connection_request_list")
            self.assertTrue(redirect_url in response["Location"])

            response = self.client.post(url)
            self.assertResponse200(response)
            self.assertTrue("errors" in response.context)
            self.assertEqual(
                response.context["errors"], ["You already requested connection from this user."]
            )

        url = reverse(
            "connection_add_connection", kwargs={"to_username": self.user_bob.username}
        )
        with self.login(self.user_amy.username, self.user_pw):
            response = self.client.post(url)
            self.assertResponse200(response)
            self.assertTrue("errors" in response.context)
            self.assertEqual(
                response.context["errors"], ["This user already requested connection from you."]
            )

    def test_connection_requests(self):
        url = reverse("connection_request_list")

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            response = self.client.get(url)
            self.assertResponse200(response)

    def test_connection_requests_rejected(self):
        url = reverse("connection_requests_rejected")

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            response = self.client.get(url)
            self.assertResponse200(response)

    def test_connection_accept(self):
        url = reverse(
            "connection_accept",
            kwargs={"connection_request_id": self.connection_request.pk},
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            # if we don't POST the view should return the
            # connection_requests_detail view
            response = self.client.get(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_requests_detail",
                kwargs={"connection_request_id": self.connection_request.pk},
            )
            self.assertTrue(redirect_url in response["Location"])

            # on POST accept the connection request and redirect to the
            # connection_view_connections view
            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_view_connections", kwargs={"username": self.user_bob.username}
            )
            self.assertTrue(redirect_url in response["Location"])

        with self.login(self.user_steve.username, self.user_pw):
            # on POST try to accept the connection request
            # but I am logged in as Steve, so I cannot accept
            # a request sent to Bob
            response = self.client.post(url)
            self.assertResponse404(response)

    def test_connection_reject(self):
        url = reverse(
            "connection_reject",
            kwargs={"connection_request_id": self.connection_request.pk},
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            # if we don't POST the view should return the
            # connection_requests_detail view
            response = self.client.get(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_requests_detail",
                kwargs={"connection_request_id": self.connection_request.pk},
            )
            self.assertTrue(redirect_url in response["Location"])

            # on POST reject the connection request and redirect to the
            # connection_requests view
            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse("connection_request_list")
            self.assertTrue(redirect_url in response["Location"])

        with self.login(self.user_steve.username, self.user_pw):
            # on POST try to reject the connection request
            # but I am logged in as Steve, so I cannot reject
            # a request sent to Bob
            response = self.client.post(url)
            self.assertResponse404(response)

    def test_connection_cancel(self):
        url = reverse(
            "connection_cancel",
            kwargs={"connection_request_id": self.connection_request.pk},
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            # if we don't POST the view should return the
            # connection_requests_detail view
            response = self.client.get(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_requests_detail",
                kwargs={"connection_request_id": self.connection_request.pk},
            )
            self.assertTrue(redirect_url in response["Location"])

            # on POST try to cancel the connection request
            # but I am logged in as Bob, so I cannot cancel
            # a request made by Steve
            response = self.client.post(url)
            self.assertResponse404(response)

        with self.login(self.user_steve.username, self.user_pw):
            # on POST cancel the connection request and redirect to the
            # connection_requests view
            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse("connection_request_list")
            self.assertTrue(redirect_url in response["Location"])

    def test_connection_requests_detail(self):
        url = reverse(
            "connection_requests_detail",
            kwargs={"connection_request_id": self.connection_request.pk},
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            response = self.client.get(url)
            self.assertResponse200(response)

    def test_connection_followers(self):
        url = reverse("connection_followers", kwargs={"username": "bob"})

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse200(response)

        with self.settings(
            CONNECTION_CONTEXT_OBJECT_NAME="object", TEMPLATE_DIRS=(TEST_TEMPLATES,)
        ):
            response = self.client.get(url)
            self.assertResponse200(response)
            self.assertTrue("object" in response.context)

    def test_connection_following(self):
        url = reverse("connection_following", kwargs={"username": "bob"})

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse200(response)

        with self.settings(
            CONNECTION_CONTEXT_OBJECT_NAME="object", TEMPLATE_DIRS=(TEST_TEMPLATES,)
        ):
            response = self.client.get(url)
            self.assertResponse200(response)
            self.assertTrue("object" in response.context)

    def test_follower_add(self):
        url = reverse(
            "follower_add", kwargs={"followee_username": self.user_amy.username}
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            response = self.client.get(url)
            self.assertResponse200(response)

            # on POST accept the connection request and redirect to the
            # connection_following view
            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_following", kwargs={"username": self.user_bob.username}
            )
            self.assertTrue(redirect_url in response["Location"])

            response = self.client.post(url)
            self.assertResponse200(response)
            self.assertTrue("errors" in response.context)
            self.assertEqual(
                response.context["errors"], ["User 'bob' already follows 'amy'"]
            )

    def test_follower_remove(self):
        # create a follow relationship so we can test removing a follower
        Follow.objects.add_follower(self.user_bob, self.user_amy)

        url = reverse(
            "follower_remove", kwargs={"followee_username": self.user_amy.username}
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            response = self.client.get(url)
            self.assertResponse200(response)

            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_following", kwargs={"username": self.user_bob.username}
            )
            self.assertTrue(redirect_url in response["Location"])

    def test_connection_blockers(self):
        url = reverse("connection_blockers", kwargs={"username": "bob"})

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse200(response)

        with self.settings(
            CONNECTION_CONTEXT_OBJECT_NAME="object", TEMPLATE_DIRS=(TEST_TEMPLATES,)
        ):
            response = self.client.get(url)
            self.assertResponse200(response)
            self.assertTrue("object" in response.context)

    def test_connection_blocking(self):
        url = reverse("connection_blocking", kwargs={"username": "bob"})

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse200(response)

        with self.settings(
            CONNECTION_CONTEXT_OBJECT_NAME="object", TEMPLATE_DIRS=(TEST_TEMPLATES,)
        ):
            response = self.client.get(url)
            self.assertResponse200(response)
            self.assertTrue("object" in response.context)

    def test_block_add(self):
        url = reverse("block_add", kwargs={"blocked_username": self.user_amy.username})

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            response = self.client.get(url)
            self.assertResponse200(response)

            # on POST accept the connection request and redirect to the
            # connection_following view
            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_blocking", kwargs={"username": self.user_bob.username}
            )
            self.assertTrue(redirect_url in response["Location"])

            response = self.client.post(url)
            self.assertResponse200(response)
            self.assertTrue("errors" in response.context)
            self.assertEqual(
                response.context["errors"], ["User 'bob' already blocks 'amy'"]
            )

    def test_block_remove(self):
        # create a follow relationship so we can test removing a block
        Block.objects.add_block(self.user_bob, self.user_amy)

        url = reverse(
            "block_remove", kwargs={"blocked_username": self.user_amy.username}
        )

        # test that the view requires authentication to access it
        response = self.client.get(url)
        self.assertResponse302(response)

        with self.login(self.user_bob.username, self.user_pw):
            response = self.client.get(url)
            self.assertResponse200(response)

            response = self.client.post(url)
            self.assertResponse302(response)
            redirect_url = reverse(
                "connection_blocking", kwargs={"username": self.user_bob.username}
            )
            self.assertTrue(redirect_url in response["Location"])

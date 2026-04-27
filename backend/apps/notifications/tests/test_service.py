import pytest
from apps.notifications.models import Notification
from apps.notifications.services import NotificationService
from conftest import UserFactory, InstitutionFactory


@pytest.mark.django_db
class TestNotificationServiceCreate:

    def test_create_notification(self, db):
        user = UserFactory()
        n = NotificationService.create(user, Notification.Type.SYSTEM, "Test", "Body")
        assert n.user == user
        assert n.title == "Test"
        assert n.is_read is False

    def test_list_recent_returns_newest_first(self, db):
        user = UserFactory()
        NotificationService.create(user, Notification.Type.SYSTEM, "First")
        NotificationService.create(user, Notification.Type.SYSTEM, "Second")
        results = list(NotificationService.list_recent(user))
        assert results[0].title == "Second"

    def test_list_recent_scoped_to_user(self, db):
        user_a = UserFactory()
        user_b = UserFactory()
        NotificationService.create(user_a, Notification.Type.SYSTEM, "Only for A")
        results = list(NotificationService.list_recent(user_b))
        assert len(results) == 0

    def test_unread_count(self, db):
        user = UserFactory()
        NotificationService.create(user, Notification.Type.SYSTEM, "One")
        NotificationService.create(user, Notification.Type.SYSTEM, "Two")
        assert NotificationService.unread_count(user) == 2

    def test_mark_read(self, db):
        user = UserFactory()
        n = NotificationService.create(user, Notification.Type.SYSTEM, "Msg")
        NotificationService.mark_read(str(n.id), user)
        n.refresh_from_db()
        assert n.is_read is True

    def test_mark_read_wrong_user_has_no_effect(self, db):
        user_a = UserFactory()
        user_b = UserFactory()
        n = NotificationService.create(user_a, Notification.Type.SYSTEM, "Msg")
        NotificationService.mark_read(str(n.id), user_b)
        n.refresh_from_db()
        assert n.is_read is False

    def test_mark_all_read(self, db):
        user = UserFactory()
        NotificationService.create(user, Notification.Type.SYSTEM, "A")
        NotificationService.create(user, Notification.Type.SYSTEM, "B")
        NotificationService.mark_all_read(user)
        assert NotificationService.unread_count(user) == 0

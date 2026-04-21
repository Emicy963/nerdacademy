"""
HTTP-layer tests for trainers endpoints.
"""

import pytest
from conftest import (
    InstitutionFactory, UserFactory, MembershipFactory,
    TrainerFactory, make_auth_client,
)


@pytest.mark.django_db
class TestTrainerListCreateView:

    URL = "/api/trainers/"

    def test_unauthenticated_returns_401(self, client):
        resp = client.get(self.URL)
        assert resp.status_code == 401

    def test_trainer_role_cannot_list(self, db, institution, trainer_user):
        client = make_auth_client(trainer_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 403

    def test_student_cannot_list(self, db, institution, student_user):
        client = make_auth_client(student_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 403

    def test_admin_can_list(self, db, institution, admin_user):
        TrainerFactory.create_batch(3, institution=institution)
        client = make_auth_client(admin_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["count"] == 3

    def test_list_scoped_to_institution(self, db, institution, admin_user):
        TrainerFactory.create_batch(2, institution=institution)
        TrainerFactory.create_batch(4, institution=InstitutionFactory())
        client = make_auth_client(admin_user, institution)
        resp = client.get(self.URL)
        assert resp.json()["count"] == 2

    def test_admin_can_create_trainer(self, db, institution, admin_user):
        client = make_auth_client(admin_user, institution)
        resp = client.post(self.URL, {
            "full_name": "Carlos Mendes",
            "specialization": "Redes",
            "email": "carlos@school.ao",
        })
        assert resp.status_code == 201
        assert resp.json()["full_name"] == "Carlos Mendes"
        assert "temp_password" in resp.json()

    def test_admin_can_create_trainer_without_email(self, db, institution, admin_user):
        client = make_auth_client(admin_user, institution)
        resp = client.post(self.URL, {"full_name": "Sem Email", "specialization": "Java"})
        assert resp.status_code == 201
        assert "temp_password" not in resp.json()

    def test_trainer_cannot_create(self, db, institution, trainer_user):
        client = make_auth_client(trainer_user, institution)
        resp = client.post(self.URL, {"full_name": "X"})
        assert resp.status_code == 403


@pytest.mark.django_db
class TestTrainerDetailView:

    def _url(self, trainer_id):
        return f"/api/trainers/{trainer_id}/"

    def test_admin_get_detail(self, db, institution, admin_user, trainer):
        client = make_auth_client(admin_user, institution)
        resp = client.get(self._url(trainer.id))
        assert resp.status_code == 200
        assert resp.json()["id"] == str(trainer.id)

    def test_trainer_cannot_get_detail(self, db, institution, trainer_user, trainer):
        client = make_auth_client(trainer_user, institution)
        resp = client.get(self._url(trainer.id))
        assert resp.status_code == 403

    def test_admin_patch(self, db, institution, admin_user, trainer):
        client = make_auth_client(admin_user, institution)
        resp = client.patch(
            self._url(trainer.id), {"full_name": "Updated Trainer"},
            format='json',
        )
        assert resp.status_code == 200
        assert resp.json()["full_name"] == "Updated Trainer"

    def test_admin_delete(self, db, institution, admin_user, trainer):
        client = make_auth_client(admin_user, institution)
        resp = client.delete(self._url(trainer.id))
        assert resp.status_code == 204

    def test_cannot_access_other_institution_trainer(self, db, institution, admin_user):
        other = TrainerFactory(institution=InstitutionFactory())
        client = make_auth_client(admin_user, institution)
        resp = client.get(self._url(other.id))
        assert resp.status_code == 404

    def test_get_nonexistent_returns_404(self, db, institution, admin_user):
        import uuid
        client = make_auth_client(admin_user, institution)
        resp = client.get(self._url(uuid.uuid4()))
        assert resp.status_code == 404


@pytest.mark.django_db
class TestMyTrainerProfileView:

    URL = "/api/trainers/me/"

    def test_trainer_sees_own_profile(self, db, institution):
        user = UserFactory()
        MembershipFactory(user=user, institution=institution, role="trainer")
        trainer = TrainerFactory(institution=institution, user=user)
        client = make_auth_client(user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 200
        assert resp.json()["id"] == str(trainer.id)

    def test_user_without_trainer_profile_returns_404(self, db, institution, trainer_user):
        client = make_auth_client(trainer_user, institution)
        resp = client.get(self.URL)
        assert resp.status_code == 404


@pytest.mark.django_db
class TestTrainerResetPasswordView:

    def _url(self, trainer_id):
        return f"/api/trainers/{trainer_id}/reset-password/"

    def test_admin_can_reset_password(self, db, institution, admin_user):
        user = UserFactory()
        MembershipFactory(user=user, institution=institution, role="trainer")
        trainer = TrainerFactory(institution=institution, user=user)
        client = make_auth_client(admin_user, institution)
        resp = client.post(self._url(trainer.id))
        assert resp.status_code == 200
        assert "temp_password" in resp.json()
        user.refresh_from_db()
        assert user.must_change_password is True
        assert user.check_password(resp.json()["temp_password"])

    def test_trainer_without_user_returns_400(self, db, institution, admin_user, trainer):
        client = make_auth_client(admin_user, institution)
        resp = client.post(self._url(trainer.id))
        assert resp.status_code == 400

    def test_non_admin_cannot_reset_password(self, db, institution, trainer_user, trainer):
        client = make_auth_client(trainer_user, institution)
        resp = client.post(self._url(trainer.id))
        assert resp.status_code == 403

    def test_cannot_reset_password_for_other_institution(self, db, institution, admin_user):
        other_trainer = TrainerFactory(institution=InstitutionFactory())
        client = make_auth_client(admin_user, institution)
        resp = client.post(self._url(other_trainer.id))
        assert resp.status_code == 404

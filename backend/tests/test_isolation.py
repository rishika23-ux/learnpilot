import uuid

from app.models.document import Document


def _create_doc_for_user(db_session, user_id):
    doc = Document(
        user_id=uuid.UUID(user_id),
        filename="secret.pdf",
        source_type="pdf",
        status="ready",
    )
    db_session.add(doc)
    db_session.commit()
    db_session.refresh(doc)
    return doc


def test_user_cannot_see_other_users_documents(client, make_user, db_session):
    user_a = make_user(email="usera@example.com")
    user_b = make_user(email="userb@example.com")

    me_a = client.get("/auth/me", headers=user_a["headers"]).json()
    doc = _create_doc_for_user(db_session, me_a["id"])

    r = client.get(f"/documents/{doc.id}", headers=user_b["headers"])
    assert r.status_code == 404

    r = client.get(f"/documents/{doc.id}", headers=user_a["headers"])
    assert r.status_code == 200


def test_document_list_only_shows_own_documents(client, make_user, db_session):
    user_a = make_user(email="usera2@example.com")
    user_b = make_user(email="userb2@example.com")

    me_a = client.get("/auth/me", headers=user_a["headers"]).json()
    _create_doc_for_user(db_session, me_a["id"])
    _create_doc_for_user(db_session, me_a["id"])

    r = client.get("/documents", headers=user_b["headers"])
    assert r.status_code == 200
    assert r.json() == []

    r = client.get("/documents", headers=user_a["headers"])
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_nonexistent_document_returns_404(client, make_user):
    user_a = make_user(email="usera3@example.com")
    fake_id = uuid.uuid4()
    r = client.get(f"/documents/{fake_id}", headers=user_a["headers"])
    assert r.status_code == 404
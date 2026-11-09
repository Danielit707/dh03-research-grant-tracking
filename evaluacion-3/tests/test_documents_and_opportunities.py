from datetime import date, timedelta
from pathlib import Path


PDF_BYTES = b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF"


def create_proposal(client, auth, opportunity_id="opp-horizon-2027"):
    response = client.post(
        "/proposals",
        headers=auth(),
        json={
            "opportunity_id": opportunity_id,
            "title": "Security validation study",
            "abstract": "Synthetic test proposal.",
            "requested_amount": 18000,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def first_requirement(client, auth, proposal_id):
    requirements = client.get(
        f"/proposals/{proposal_id}/documents", headers=auth()
    )
    assert requirements.status_code == 200
    return next(item for item in requirements.json() if item["required"])


def test_opportunity_catalog_uses_only_the_standard_proposal_documents(client):
    first_page = client.get("/opportunities")
    assert first_page.status_code == 200
    assert len(first_page.json()["items"]) == 6
    assert first_page.json()["total_pages"] >= 4
    second_page = client.get("/opportunities?page=2&page_size=6").json()
    assert not {
        item["id"] for item in first_page.json()["items"]
    } & {item["id"] for item in second_page["items"]}

    response = client.get("/opportunities?page=1&page_size=50")
    assert response.status_code == 200
    opportunities = response.json()["items"]
    assert len(opportunities) >= 20
    assert all(item["status"] == "OPEN" for item in opportunities)
    assert all(item["deadline"] for item in opportunities)
    counts = {item["required_document_count"] for item in opportunities}
    assert min(counts) == 3
    assert max(counts) == 4
    expected = {"Propuesta técnica", "Documentos administrativos", "Presupuesto"}
    conditional = {"Ética y compliance", "Revisión de compromisos académicos"}
    assert all(expected.issubset({doc["name"] for doc in item["documents"]}) for item in opportunities)
    assert all(
        ({doc["name"] for doc in item["documents"]} - expected).issubset(conditional)
        for item in opportunities
    )
    assert all(all(doc["required"] for doc in item["documents"]) for item in opportunities)
    by_id = {item["id"]: item for item in opportunities}
    assert "Ética y compliance" in {doc["name"] for doc in by_id["opp-biomedical"]["documents"]}
    assert "Revisión de compromisos académicos" in {
        doc["name"] for doc in by_id["opp-equipment"]["documents"]
    }
    assert all(item["description"] for item in opportunities)
    assert "opp-closed-deadline" not in {item["id"] for item in opportunities}


def test_coordinator_assignment_is_explicit_and_scoped(client, auth):
    proposal = create_proposal(client, auth)
    proposal_id = proposal["id"]

    queue = client.get("/coordinator-assignments", headers=auth("demo-coordinator"))
    assert queue.status_code == 200
    assert proposal_id not in {item["id"] for item in queue.json()}
    draft_claim = client.post(
        f"/proposals/{proposal_id}/coordinator-assignment",
        headers=auth("demo-coordinator"),
    )
    assert draft_claim.status_code == 409
    assert draft_claim.json()["error"]["code"] == "proposal_not_ready_for_assignment"

    requirements = client.get(f"/proposals/{proposal_id}/documents", headers=auth()).json()
    for requirement in requirements:
        uploaded = client.post(
            f"/proposals/{proposal_id}/documents/{requirement['requirement_id']}",
            headers=auth(),
            files={"file": ("required.pdf", PDF_BYTES, "application/pdf")},
        )
        assert uploaded.status_code == 201
    sent = client.post(
        f"/proposals/{proposal_id}/submit", headers=auth(), json={"expected_version": 0}
    )
    assert sent.status_code == 200

    queue = client.get("/coordinator-assignments", headers=auth("demo-coordinator"))
    queued = next(item for item in queue.json() if item["id"] == proposal_id)
    assert queued["abstract"] == "Synthetic test proposal."
    assert queued["opportunity_description"]
    assert "requested_amount" not in queued

    assigned = client.post(
        f"/proposals/{proposal_id}/coordinator-assignment",
        headers=auth("demo-coordinator-mateo"),
    )
    assert assigned.status_code == 201
    assert assigned.json()["coordinator_id"] == "user-coordinator-2"

    alice_proposals = client.get("/proposals", headers=auth()).json()
    assert any(item["id"] == proposal_id for item in alice_proposals)
    camila_proposals = client.get("/proposals", headers=auth("demo-coordinator")).json()
    assert all(item["id"] != proposal_id for item in camila_proposals)
    mateo_proposals = client.get("/proposals", headers=auth("demo-coordinator-mateo")).json()
    assert any(item["id"] == proposal_id for item in mateo_proposals)


def test_changes_required_returns_same_proposal_to_pi_for_revision_and_resubmission(client, auth):
    proposal = create_proposal(client, auth)
    proposal_id = proposal["id"]
    requirements = client.get(f"/proposals/{proposal_id}/documents", headers=auth()).json()
    for requirement in requirements:
        uploaded = client.post(
            f"/proposals/{proposal_id}/documents/{requirement['requirement_id']}",
            headers=auth(), files={"file": ("initial.pdf", PDF_BYTES, "application/pdf")},
        )
        assert uploaded.status_code == 201
    first_submission = client.post(
        f"/proposals/{proposal_id}/submit", headers=auth(), json={"expected_version": 0}
    )
    assert first_submission.status_code == 200

    assigned = client.post(
        f"/proposals/{proposal_id}/coordinator-assignment", headers=auth("demo-coordinator")
    )
    assert assigned.status_code == 201
    requested = client.put(
        f"/proposals/{proposal_id}/document-verification",
        headers=auth("demo-coordinator"),
        json={
            "status": "CHANGES_REQUIRED",
            "notes": "Actualiza el presupuesto y vuelve a enviarlo.",
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
        },
    )
    assert requested.status_code == 200
    returned = client.get(f"/proposals/{proposal_id}", headers=auth()).json()
    assert returned["status"] == "DRAFT"
    assert returned["submitted_version_id"] is None

    budget = next(item for item in requirements if item["name"] == "Presupuesto")
    revision = client.post(
        f"/proposals/{proposal_id}/documents/{budget['requirement_id']}",
        headers=auth(), files={"file": ("revised-budget.pdf", PDF_BYTES, "application/pdf")},
    )
    assert revision.status_code == 201
    assert revision.json()["version"] == 2
    second_submission = client.post(
        f"/proposals/{proposal_id}/submit", headers=auth(), json={"expected_version": 1}
    )
    assert second_submission.status_code == 200
    assert second_submission.json()["id"] == proposal_id
    assert second_submission.json()["status"] == "SUBMITTED"
    verification = client.get(
        f"/proposals/{proposal_id}/document-verification", headers=auth()
    ).json()
    assert verification["status"] == "PENDING"
    assert verification["notes"] == ""


def test_pi_can_delete_own_proposal_and_all_related_state_and_files(client, auth, database):
    proposal = create_proposal(client, auth)
    proposal_id = proposal["id"]
    requirements = client.get(f"/proposals/{proposal_id}/documents", headers=auth()).json()
    for requirement in requirements:
        upload = client.post(
            f"/proposals/{proposal_id}/documents/{requirement['requirement_id']}",
            headers=auth(), files={"file": ("evidence.pdf", PDF_BYTES, "application/pdf")},
        )
        assert upload.status_code == 201
    assert client.post(
        f"/proposals/{proposal_id}/submit", headers=auth(), json={"expected_version": 0}
    ).status_code == 200

    denied = client.delete(f"/proposals/{proposal_id}", headers=auth("demo-pi-bob"))
    assert denied.status_code == 403

    with database.read() as connection:
        keys = [row["storage_key"] for row in connection.execute(
            "SELECT storage_key FROM proposal_documents WHERE proposal_id = ?", (proposal_id,)
        )]
    objects = Path(database.path).parent / "private-documents" / "objects"
    stored_paths = [objects / key for key in keys]
    assert all(path.is_file() for path in stored_paths)

    deleted = client.delete(f"/proposals/{proposal_id}", headers=auth())
    assert deleted.status_code == 200
    assert deleted.json() == {"proposal_id": proposal_id, "deleted": True}
    assert client.get(f"/proposals/{proposal_id}", headers=auth()).status_code == 404
    assert all(not path.exists() for path in stored_paths)
    with database.read() as connection:
        for table in (
            "proposal_memberships", "proposal_versions", "proposal_documents",
            "document_verifications", "notification_outbox", "audit_events",
        ):
            count = connection.execute(
                f"SELECT COUNT(*) FROM {table} WHERE "
                + ("proposal_id = ?" if table in {
                    "proposal_memberships", "proposal_versions", "proposal_documents",
                    "document_verifications",
                } else "aggregate_id = ?" if table == "notification_outbox"
                else "entity_id = ?"),
                (proposal_id,),
            ).fetchone()[0]
            assert count == 0, table


def test_submission_is_blocked_until_each_required_document_is_uploaded(client, auth):
    proposal = create_proposal(client, auth)
    proposal_id = proposal["id"]

    blocked = client.post(
        f"/proposals/{proposal_id}/submit",
        headers=auth(),
        json={"expected_version": 0},
    )
    assert blocked.status_code == 422
    assert blocked.json()["error"]["code"] == "missing_required_documents"
    assert client.get(f"/proposals/{proposal_id}", headers=auth()).json()["status"] == "DRAFT"

    documents = client.get(f"/proposals/{proposal_id}/documents", headers=auth()).json()
    for requirement in documents:
        if requirement["required"]:
            uploaded = client.post(
                f"/proposals/{proposal_id}/documents/{requirement['requirement_id']}",
                headers=auth(),
                files={"file": ("evidence.pdf", PDF_BYTES, "application/pdf")},
            )
            assert uploaded.status_code == 201, uploaded.text

    submitted = client.post(
        f"/proposals/{proposal_id}/submit",
        headers=auth(),
        json={"expected_version": 0},
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "SUBMITTED"


def test_upload_rejects_fake_pdf_before_it_is_stored(client, auth, database):
    proposal = create_proposal(client, auth)
    requirement = first_requirement(client, auth, proposal["id"])
    upload_url = f"/proposals/{proposal['id']}/documents/{requirement['requirement_id']}"

    response = client.post(
        upload_url,
        headers=auth(),
        files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_pdf_signature"
    objects = Path(database.path).parent / "private-documents" / "objects"
    staging = Path(database.path).parent / "private-documents" / "staging"
    assert list(objects.iterdir()) == []
    assert list(staging.iterdir()) == []


def test_upload_enforces_streamed_file_size_limit(client, auth, database):
    proposal = create_proposal(client, auth)
    requirement = first_requirement(client, auth, proposal["id"])
    oversized_pdf = b"%PDF-1.7\n" + b"x" * (10 * 1024 * 1024) + b"\n%%EOF"
    response = client.post(
        f"/proposals/{proposal['id']}/documents/{requirement['requirement_id']}",
        headers=auth(),
        files={"file": ("too-large.pdf", oversized_pdf, "application/pdf")},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "document_too_large"
    objects = Path(database.path).parent / "private-documents" / "objects"
    staging = Path(database.path).parent / "private-documents" / "staging"
    assert list(objects.iterdir()) == []
    assert list(staging.iterdir()) == []


def test_upload_requires_pdf_extension_and_owner_permission(client, auth):
    proposal = create_proposal(client, auth)
    requirement = first_requirement(client, auth, proposal["id"])
    upload_url = f"/proposals/{proposal['id']}/documents/{requirement['requirement_id']}"

    wrong_extension = client.post(
        upload_url,
        headers=auth(),
        files={"file": ("payload.exe", PDF_BYTES, "application/pdf")},
    )
    assert wrong_extension.status_code == 422
    assert wrong_extension.json()["error"]["code"] == "invalid_document_filename"

    forbidden = client.post(
        upload_url,
        headers=auth("demo-pi-bob"),
        files={"file": ("valid.pdf", PDF_BYTES, "application/pdf")},
    )
    assert forbidden.status_code == 403


def test_upload_is_private_versioned_and_only_downloaded_by_proposal_members(client, auth, database):
    proposal = create_proposal(client, auth)
    proposal_id = proposal["id"]
    requirement = first_requirement(client, auth, proposal_id)
    upload_url = f"/proposals/{proposal_id}/documents/{requirement['requirement_id']}"

    first = client.post(
        upload_url,
        headers=auth(),
        files={"file": ("../budget.pdf", PDF_BYTES, "application/pdf")},
    )
    assert first.status_code == 201
    first_document = first.json()
    assert first_document["filename"] == "budget.pdf"
    assert first_document["version"] == 1

    second = client.post(
        upload_url,
        headers=auth(),
        files={"file": ("budget-revised.pdf", PDF_BYTES, "application/pdf")},
    )
    assert second.status_code == 201
    assert second.json()["version"] == 2

    denied = client.get(
        f"/proposals/{proposal_id}/documents/{second.json()['id']}/download",
        headers=auth("demo-pi-bob"),
    )
    assert denied.status_code == 403

    downloaded = client.get(
        f"/proposals/{proposal_id}/documents/{second.json()['id']}/download",
        headers=auth(),
    )
    assert downloaded.status_code == 200
    assert downloaded.content == PDF_BYTES
    assert downloaded.headers["content-type"] == "application/octet-stream"
    assert downloaded.headers["x-content-type-options"] == "nosniff"
    assert "attachment" in downloaded.headers["content-disposition"]

    with database.read() as connection:
        record = connection.execute(
            "SELECT storage_key FROM proposal_documents WHERE id = ?",
            (second.json()["id"],),
        ).fetchone()
    stored_path = Path(database.path).parent / "private-documents" / "objects" / record["storage_key"]
    assert stored_path.is_file()
    assert "static" not in stored_path.parts


def test_complete_verification_locks_proposal_and_records_correction_history(client, auth):
    proposal = create_proposal(client, auth)
    proposal_id = proposal["id"]
    requirements = client.get(f"/proposals/{proposal_id}/documents", headers=auth()).json()
    for requirement in requirements:
        uploaded = client.post(
            f"/proposals/{proposal_id}/documents/{requirement['requirement_id']}",
            headers=auth(),
            files={"file": ("initial.pdf", PDF_BYTES, "application/pdf")},
        )
        assert uploaded.status_code == 201
    assert client.post(
        f"/proposals/{proposal_id}/submit", headers=auth(), json={"expected_version": 0}
    ).status_code == 200
    assert client.post(
        f"/proposals/{proposal_id}/coordinator-assignment", headers=auth("demo-coordinator")
    ).status_code == 201

    correction = client.put(
        f"/proposals/{proposal_id}/document-verification",
        headers=auth("demo-coordinator"),
        json={
            "status": "CHANGES_REQUIRED",
            "notes": "Reemplaza el presupuesto con la versión firmada.",
            "due_date": (date.today() + timedelta(days=5)).isoformat(),
        },
    )
    assert correction.status_code == 200
    budget = next(item for item in requirements if item["name"] == "Presupuesto")
    assert client.post(
        f"/proposals/{proposal_id}/documents/{budget['requirement_id']}",
        headers=auth(),
        files={"file": ("budget-signed.pdf", PDF_BYTES, "application/pdf")},
    ).status_code == 201
    assert client.post(
        f"/proposals/{proposal_id}/submit", headers=auth(), json={"expected_version": 1}
    ).status_code == 200

    verified = client.put(
        f"/proposals/{proposal_id}/document-verification",
        headers=auth("demo-coordinator"),
        json={"status": "COMPLETE", "notes": "Todos los documentos obligatorios fueron verificados."},
    )
    assert verified.status_code == 200
    locked = client.get(f"/proposals/{proposal_id}", headers=auth()).json()
    assert locked["status"] == "VERIFIED"

    denied_delete = client.delete(f"/proposals/{proposal_id}", headers=auth())
    assert denied_delete.status_code == 409
    assert denied_delete.json()["error"]["code"] == "proposal_locked_after_verification"

    denied_review = client.put(
        f"/proposals/{proposal_id}/document-verification",
        headers=auth("demo-coordinator"),
        json={"status": "PENDING", "notes": "Reabrir", "due_date": date.today().isoformat()},
    )
    assert denied_review.status_code == 409
    assert denied_review.json()["error"]["code"] == "proposal_locked_after_verification"

    events = client.get(f"/proposals/{proposal_id}/audit", headers=auth()).json()
    correction_event = next(
        event for event in events
        if event["event_type"] == "documents.verification_updated"
        and event["details"]["status"] == "CHANGES_REQUIRED"
    )
    assert correction_event["details"]["notes"] == "Reemplaza el presupuesto con la versión firmada."
    assert correction_event["details"]["reason"]
    assert {item["name"] for item in correction_event["details"]["documents"]} >= {
        "Presupuesto", "Propuesta técnica", "Documentos administrativos"
    }
    upload_event = next(
        event for event in reversed(events)
        if event["event_type"] == "proposal.document_uploaded"
        and event["details"].get("requirement_name") == "Presupuesto"
    )
    assert upload_event["details"]["filename"] == "budget-signed.pdf"
    assert upload_event["details"]["previous_version"] == 1
    assert any(item.get("filename") == "budget-signed.pdf" for item in upload_event["details"]["documents"])
    complete_event = next(
        event for event in events
        if event["event_type"] == "documents.verification_updated"
        and event["details"]["status"] == "COMPLETE"
    )
    assert complete_event["details"]["previous_status"] == "PENDING"
    assert all(item["document_id"] for item in complete_event["details"]["documents"])

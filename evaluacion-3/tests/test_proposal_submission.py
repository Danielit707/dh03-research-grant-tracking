from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import hashlib
import json


def complete_proposal(opportunity_id="opp-horizon-2027"):
    return {
        "opportunity_id": opportunity_id,
        "title": "Community solar storage pilot",
        "abstract": "Evaluate a synthetic community-scale energy storage design.",
        "requested_amount": 42500.0,
    }


def upload_required_documents(client, auth, proposal_id):
    requirements = client.get(
        f"/proposals/{proposal_id}/documents", headers=auth()
    ).json()
    for requirement in requirements:
        if requirement["required"] and not requirement["uploaded"]:
            response = client.post(
                f"/proposals/{proposal_id}/documents/{requirement['requirement_id']}",
                headers=auth(),
                files={"file": ("synthetic-evidence.pdf", b"%PDF-1.7\n1 0 obj\n<<>>\nendobj\n%%EOF", "application/pdf")},
            )
            assert response.status_code == 201, response.text


def test_submission_persists_exact_version_audit_and_outbox(client, auth, database):
    created = client.post("/proposals", headers=auth(), json=complete_proposal())
    assert created.status_code == 201
    proposal_id = created.json()["id"]
    upload_required_documents(client, auth, proposal_id)

    submitted = client.post(
        f"/proposals/{proposal_id}/submit",
        headers=auth(),
        json={"expected_version": 0},
    )
    assert submitted.status_code == 200
    result = submitted.json()
    assert result["status"] == "SUBMITTED"
    assert result["version"] == 1
    assert result["submitted_version_id"]

    version_response = client.get(
        f"/proposals/{proposal_id}/versions/{result['submitted_version_id']}",
        headers=auth(),
    )
    assert version_response.status_code == 200
    version = version_response.json()
    assert version["snapshot"]["title"] == "Community solar storage pilot"
    expected_hash = hashlib.sha256(
        json.dumps(version["snapshot"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()
    assert version["content_hash"] == expected_hash

    events = client.get(f"/proposals/{proposal_id}/audit", headers=auth()).json()
    submission_events = [event for event in events if event["event_type"] == "proposal.submitted"]
    assert len(submission_events) == 1
    assert submission_events[0]["actor_id"] == "user-alice"
    assert submission_events[0]["details"]["version_id"] == result["submitted_version_id"]

    with database.read() as connection:
        outbox = connection.execute(
            """
            SELECT event_type, aggregate_id, payload_json
            FROM notification_outbox WHERE event_key = ?
            """,
            (submission_events[0]["id"],),
        ).fetchone()
        assert outbox["event_type"] == "proposal.submitted"
        assert outbox["aggregate_id"] == proposal_id
        assert json.loads(outbox["payload_json"])["version_id"] == result["submitted_version_id"]


def test_incomplete_submission_is_rejected_without_partial_state(client, auth, database):
    created = client.post(
        "/proposals",
        headers=auth(),
        json={"opportunity_id": "opp-horizon-2027", "title": "Incomplete draft"},
    )
    proposal_id = created.json()["id"]
    response = client.post(
        f"/proposals/{proposal_id}/submit",
        headers=auth(),
        json={"expected_version": 0},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "incomplete_proposal"
    unchanged = client.get(f"/proposals/{proposal_id}", headers=auth()).json()
    assert unchanged["status"] == "DRAFT"
    assert unchanged["version"] == 0
    with database.read() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM proposal_versions WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()[0] == 0
        assert connection.execute(
            """
            SELECT COUNT(*) FROM notification_outbox o
            JOIN audit_events a ON a.id = o.event_key
            WHERE a.entity_id = ? AND a.event_type = 'proposal.submitted'
            """,
            (proposal_id,),
        ).fetchone()[0] == 0

    repaired = client.patch(
        f"/proposals/{proposal_id}",
        headers=auth(),
        json={
            "expected_version": 0,
            "abstract": "A complete synthetic proposal description.",
            "requested_amount": 12000,
        },
    )
    assert repaired.status_code == 200
    assert repaired.json()["version"] == 1
    upload_required_documents(client, auth, proposal_id)
    submitted = client.post(
        f"/proposals/{proposal_id}/submit",
        headers=auth(),
        json={"expected_version": 1},
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "SUBMITTED"
    assert submitted.json()["version"] == 2


def test_closed_or_expired_opportunity_cannot_be_applied_to(client, auth):
    response = client.post(
        "/proposals", headers=auth(), json=complete_proposal("opp-closed-deadline")
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "opportunity_closed"


def test_pi_cannot_read_or_submit_another_pis_proposal(client, auth):
    denied_read = client.get("/proposals/proposal-seed-bob", headers=auth("demo-pi-alice"))
    assert denied_read.status_code == 403
    assert "title" not in denied_read.json()

    denied_submit = client.post(
        "/proposals/proposal-seed-bob/submit",
        headers=auth("demo-pi-alice"),
        json={"expected_version": 0},
    )
    assert denied_submit.status_code == 403
    assert denied_submit.json()["error"]["code"] == "forbidden"


def test_coordinator_role_cannot_submit_as_a_pi(client, auth):
    denied = client.post(
        "/proposals/proposal-seed-alice/submit",
        headers=auth("demo-coordinator"),
        json={"expected_version": 0},
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "forbidden"


def test_repeated_submission_is_rejected_as_invalid_transition(client, auth, database):
    proposal_id = "proposal-seed-alice"
    upload_required_documents(client, auth, proposal_id)
    first = client.post(
        f"/proposals/{proposal_id}/submit",
        headers=auth(),
        json={"expected_version": 0},
    )
    assert first.status_code == 200

    second = client.post(
        f"/proposals/{proposal_id}/submit",
        headers=auth(),
        json={"expected_version": 1},
    )
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "invalid_state_transition"
    edit_after_submit = client.patch(
        f"/proposals/{proposal_id}",
        headers=auth(),
        json={"expected_version": 1, "title": "Changed after submission"},
    )
    assert edit_after_submit.status_code == 409
    assert edit_after_submit.json()["error"]["code"] == "invalid_state_transition"
    with database.read() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM proposal_versions WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()[0] == 1
        assert connection.execute(
            """
            SELECT COUNT(*) FROM audit_events
            WHERE entity_id = ? AND event_type = 'proposal.submitted'
            """,
            (proposal_id,),
        ).fetchone()[0] == 1


def test_concurrent_submissions_have_one_winner_and_one_stale_conflict(client, auth, database):
    proposal_id = "proposal-seed-alice"
    upload_required_documents(client, auth, proposal_id)

    def submit():
        return client.post(
            f"/proposals/{proposal_id}/submit",
            headers=auth(),
            json={"expected_version": 0},
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        responses = list(pool.map(lambda _: submit(), range(2)))

    assert sorted(response.status_code for response in responses) == [200, 409]
    assert "stale_proposal_version" in {
        response.json().get("error", {}).get("code") for response in responses
    }
    with database.read() as connection:
        assert connection.execute(
            "SELECT COUNT(*) FROM proposal_versions WHERE proposal_id = ?", (proposal_id,)
        ).fetchone()[0] == 1
        assert connection.execute(
            """
            SELECT COUNT(*) FROM audit_events
            WHERE entity_id = ? AND event_type = 'proposal.submitted'
            """,
            (proposal_id,),
        ).fetchone()[0] == 1
        assert connection.execute(
            """
            SELECT COUNT(*) FROM notification_outbox o
            JOIN audit_events a ON a.id = o.event_key
            WHERE a.entity_id = ? AND a.event_type = 'proposal.submitted'
            """,
            (proposal_id,),
        ).fetchone()[0] == 1

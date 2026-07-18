import datetime


def test_end_to_end_syllabus_and_plan_flow(client):
    # 1. Register and login user
    signup_resp = client.post(
        "/api/v1/auth/signup",
        json={"email": "student@example.com", "password": "password123", "name": "Active Student"}
    )
    assert signup_resp.status_code == 201

    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "student@example.com", "password": "password123"}
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Ingest a syllabus
    raw_syllabus = (
        "Unit 1: Programming Basics\n"
        "- Variables and logic\n"
        "- Control structures"
    )
    syllabus_resp = client.post(
        "/api/v1/syllabi/",
        json={"raw_text": raw_syllabus},
        headers=headers
    )
    assert syllabus_resp.status_code == 201
    syllabus_data = syllabus_resp.json()
    assert syllabus_data["raw_text"] == raw_syllabus
    
    # Ensure it was parsed dynamically
    parsed_tree = syllabus_data["parsed_tree_json"]
    assert len(parsed_tree) == 1
    assert parsed_tree[0]["title"] == "Unit 1: Programming Basics"
    assert len(parsed_tree[0]["children"]) == 2
    assert parsed_tree[0]["children"][0]["title"] == "Variables and logic"

    # 3. Generate a study plan
    # Total of 3 days (spaced planning since we have 2 leaf topics)
    start_date = datetime.date.today().isoformat()
    end_date = (datetime.date.today() + datetime.timedelta(days=2)).isoformat()
    
    plan_resp = client.post(
        "/api/v1/plans/",
        json={
            "syllabus_id": syllabus_data["id"],
            "start_date": start_date,
            "end_date": end_date
        },
        headers=headers
    )
    assert plan_resp.status_code == 201
    plan_data = plan_resp.json()
    assert plan_data["syllabus_id"] == syllabus_data["id"]
    assert plan_data["status"] == "active"
    
    schedule = plan_data["plan_json"]
    assert len(schedule) == 3
    assert schedule[0]["day_number"] == 1
    assert len(schedule[0]["topics"]) == 1
    assert schedule[0]["topics"][0]["title"] == "Variables and logic"

    # 4. Log progress progress check-in
    progress_date = start_date
    progress_resp = client.post(
        f"/api/v1/progress/{plan_data['id']}",
        json={
            "date": progress_date,
            "completed_hours": 1.5,
            "completed_topics": [schedule[0]["topics"][0]["id"]],
            "check_in_note": "Felt good, completed variables!"
        },
        headers=headers
    )
    assert progress_resp.status_code == 201
    progress_data = progress_resp.json()
    assert progress_data["completed_hours"] == 1.5
    assert progress_data["completed_topics"] == [schedule[0]["topics"][0]["id"]]

    # 5. Fetch plan progress history
    history_resp = client.get(
        f"/api/v1/progress/{plan_data['id']}",
        headers=headers
    )
    assert history_resp.status_code == 200
    history_data = history_resp.json()
    assert len(history_data) == 1
    assert history_data[0]["check_in_note"] == "Felt good, completed variables!"

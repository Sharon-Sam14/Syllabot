def test_signup_success(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "testuser@example.com", "password": "securepassword123", "name": "Test User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert data["name"] == "Test User"
    assert "id" in data
    assert "hashed_password" not in data


def test_signup_duplicate_email(client):
    # Register first time
    response = client.post(
        "/api/v1/auth/signup",
        json={"email": "duplicate@example.com", "password": "password123", "name": "First"}
    )
    assert response.status_code == 201

    # Attempt registration with duplicate email
    response_dup = client.post(
        "/api/v1/auth/signup",
        json={"email": "duplicate@example.com", "password": "password456", "name": "Second"}
    )
    assert response_dup.status_code == 400
    assert response_dup.json()["detail"] == "The user with this email already exists in the system."


def test_login_success(client):
    # Register user
    client.post(
        "/api/v1/auth/signup",
        json={"email": "loginuser@example.com", "password": "secretpassword", "name": "Login User"}
    )

    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser@example.com", "password": "secretpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    # Register user
    client.post(
        "/api/v1/auth/signup",
        json={"email": "loginuser2@example.com", "password": "secretpassword", "name": "Login User 2"}
    )

    # Login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser2@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect email or password"

    # Login with non-existing email
    response_none = client.post(
        "/api/v1/auth/login",
        data={"username": "doesnotexist@example.com", "password": "somepassword"}
    )
    assert response_none.status_code == 400
    assert response_none.json()["detail"] == "Incorrect email or password"


def test_get_me_success(client):
    # Register user
    client.post(
        "/api/v1/auth/signup",
        json={"email": "meuser@example.com", "password": "mypassword", "name": "Me User"}
    )

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "meuser@example.com", "password": "mypassword"}
    )
    token = login_response.json()["access_token"]

    # Fetch profile using bearer token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "meuser@example.com"
    assert data["name"] == "Me User"


def test_get_me_unauthorized(client):
    # Try fetching profile without auth header
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401

    # Try fetching with invalid authorization token
    headers = {"Authorization": "Bearer invalidtoken123"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401

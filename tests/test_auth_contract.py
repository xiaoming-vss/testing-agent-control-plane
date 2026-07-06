from testing_agent.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UpdateProfileRequest,
    UserResponse,
)


def test_auth_requests_use_go_field_names():
    assert RegisterRequest.model_validate(
        {"name": "alice", "password": "secret", "email": "a@example.com"}
    ).name == "alice"
    assert LoginRequest.model_validate({"name": "alice", "password": "secret"}).name == "alice"
    assert UpdateProfileRequest.model_validate({"name": "new"}).name == "new"


def test_auth_responses_use_go_field_names():
    assert LoginResponse(access_token="token").model_dump(by_alias=True) == {
        "accessToken": "token"
    }
    assert UserResponse(user_id="u1", name="alice", email="a@example.com").model_dump(
        by_alias=True
    ) == {
        "userId": "u1",
        "name": "alice",
        "email": "a@example.com",
    }

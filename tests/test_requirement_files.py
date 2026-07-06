from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from testing_agent.api.deps import get_current_user_id, get_requirement_service
from testing_agent.app import create_app
from testing_agent.schemas.requirement import CreateRequirementRequest, UpdateRequirementRequest
from testing_agent.services.requirement import RequirementService


class FakeRequirementRepository:
    def __init__(self):
        self.requirement = None
        self.existing = None
        self.restored = None

    async def get_active_by_sprint_and_name(self, sprint_id, name):
        if self.existing is not None and getattr(self.existing, "deleted_at", None) is None:
            return self.existing
        return None

    async def get_by_sprint_and_name_unscoped(self, sprint_id, name):
        return self.existing

    async def get_active_by_id(self, requirement_id):
        return self.requirement

    def add(self, requirement):
        self.requirement = requirement

    def restore(self, requirement):
        requirement.deleted_at = None
        self.restored = requirement
        self.requirement = requirement

    async def commit(self):
        return None

    async def refresh(self, requirement):
        return None

    def soft_delete(self, requirement, deleted_at):
        requirement.deleted_at = deleted_at


class FakeSprintService:
    async def get_owned_entity(self, user_id, sprint_id):
        return SimpleNamespace(sprint_id=sprint_id, project_id="project-1")


@pytest.mark.asyncio
async def test_requirement_create_writes_text_source_to_file_without_confirmed_content(tmp_path):
    repository = FakeRequirementRepository()
    service = RequirementService(repository, FakeSprintService(), storage_root=tmp_path)

    payload = await service.create(
        "user-1",
        "sprint-1",
        CreateRequirementRequest(
            name="Login",
            documentType="text",
            documentContent="Login requirement",
        ),
    )

    storage_path = tmp_path / "requirements" / payload["requirementId"] / "requirement.txt"
    assert storage_path.read_text(encoding="utf-8") == "Login requirement"
    assert payload["documentContent"] == ""
    assert repository.requirement.document_content == ""
    assert payload["documentFilename"] == "requirement.txt"
    assert "documentContentType" not in payload
    assert "documentSize" not in payload
    assert not hasattr(repository.requirement, "document_content_type")
    assert not hasattr(repository.requirement, "document_size")
    assert payload["documentDownloadUrl"] == f"/v1/requirements/{payload['requirementId']}/download"


def test_requirement_request_rejects_richtext_document_type():
    with pytest.raises(ValidationError):
        CreateRequirementRequest(
            name="Login",
            documentType="richtext",
            documentContent="<h1>Login requirement</h1>",
        )


def test_requirement_request_accepts_docx_and_normalizes_legacy_word():
    docx_body = CreateRequirementRequest(
        name="Login",
        documentType="docx",
        documentContent="",
    )
    legacy_body = CreateRequirementRequest(
        name="Login",
        documentType="word",
        documentContent="",
    )

    assert docx_body.document_type == "docx"
    assert legacy_body.document_type == "docx"


@pytest.mark.asyncio
async def test_requirement_create_restores_soft_deleted_same_name(tmp_path):
    repository = FakeRequirementRepository()
    repository.existing = SimpleNamespace(
        requirement_id="requirement-old",
        sprint_id="sprint-1",
        name="Login",
        document_type="text",
        document_content="",
        document_filename="old.txt",
        document_hash="old-hash",
        document_storage_path="old-path",
        document_download_url="/v1/requirements/requirement-old/download",
        source_type="manual",
        binding_status="unbound",
        last_bound_at=None,
        last_binding_sync_error="",
        deleted_at="2026-01-01T00:00:00Z",
        created_at=None,
        updated_at=None,
    )
    service = RequirementService(repository, FakeSprintService(), storage_root=tmp_path)

    payload = await service.create(
        "user-1",
        "sprint-1",
        CreateRequirementRequest(
            name="Login",
            documentType="docx",
            documentContent="",
        ),
        document_file=SimpleNamespace(
            filename="requirement.docx",
            content=b"new-docx-bytes",
        ),
    )

    assert repository.restored.requirement_id == "requirement-old"
    assert repository.restored.deleted_at is None
    assert repository.restored.document_type == "docx"
    assert payload["requirementId"] == "requirement-old"
    storage_path = tmp_path / "requirements" / "requirement-old" / "requirement.docx"
    assert storage_path.read_bytes() == b"new-docx-bytes"


def test_requirement_download_endpoint_returns_stored_file():
    class FakeRequirementService:
        async def get_download(self, user_id, requirement_id):
            assert user_id == "user-1"
            assert requirement_id == "requirement-1"
            return SimpleNamespace(
                document_storage_path="",
                document_filename="requirement.txt",
                content=b"requirement file",
            )

    app = create_app()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_requirement_service] = lambda: FakeRequirementService()
    client = TestClient(app)

    response = client.get("/v1/requirements/requirement-1/download")

    assert response.status_code == 200
    assert response.content == b"requirement file"
    assert response.headers["content-type"] == "application/octet-stream"


def test_requirement_upload_create_endpoint_accepts_docx_file():
    class FakeRequirementService:
        async def create(self, user_id, sprint_id, body, document_file=None):
            assert user_id == "user-1"
            assert sprint_id == "sprint-1"
            assert body.name == "Login"
            assert body.document_type == "docx"
            assert body.document_content == ""
            assert document_file.filename == "requirement.docx"
            assert document_file.content == b"docx-bytes"
            return {
                "requirementId": "requirement-1",
                "sprintId": sprint_id,
                "name": body.name,
                "documentType": body.document_type,
                "documentContent": body.document_content,
                "documentFilename": document_file.filename,
                "documentHash": "hash",
                "documentDownloadUrl": "/v1/requirements/requirement-1/download",
                "createdAt": "",
                "updatedAt": "",
            }

    app = create_app()
    app.dependency_overrides[get_current_user_id] = lambda: "user-1"
    app.dependency_overrides[get_requirement_service] = lambda: FakeRequirementService()
    client = TestClient(app)

    response = client.post(
        "/v1/sprints/sprint-1/requirements/upload",
        data={
            "name": "Login",
            "documentType": "docx",
            "documentContent": "parsed text",
        },
        files={
            "file": (
                "requirement.docx",
                b"docx-bytes",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 0
    assert payload["data"]["documentFilename"] == "requirement.docx"
    assert "documentContentType" not in payload["data"]
    assert "documentSize" not in payload["data"]
    assert "description" not in payload["data"]
    assert "status" not in payload["data"]
    assert payload["data"]["documentDownloadUrl"] == "/v1/requirements/requirement-1/download"


@pytest.mark.asyncio
async def test_requirement_update_document_content_preserves_source_file(tmp_path):
    repository = FakeRequirementRepository()
    service = RequirementService(repository, FakeSprintService(), storage_root=tmp_path)

    payload = await service.create(
        "user-1",
        "sprint-1",
        CreateRequirementRequest(
            name="Login",
            documentType="docx",
            documentContent="",
        ),
        document_file=SimpleNamespace(
            filename="requirement.docx",
            content=b"original-docx-bytes",
        ),
    )
    storage_path = tmp_path / "requirements" / payload["requirementId"] / "requirement.docx"

    updated = await service.update(
        "user-1",
        payload["requirementId"],
        UpdateRequirementRequest(documentContent="parsed requirement text"),
    )

    assert storage_path.read_bytes() == b"original-docx-bytes"
    assert updated["documentContent"] == "parsed requirement text"
    assert updated["documentFilename"] == "requirement.docx"
    assert "documentSize" not in updated
    assert not hasattr(repository.requirement, "document_size")

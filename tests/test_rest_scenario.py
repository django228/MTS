"""Связанный REST-сценарий: POST → id → PATCH → GET."""

import uuid

import pytest

pytestmark = pytest.mark.rest

NEW_TITLE = "Updated via automated PATCH"
MISSING_POST_ID = f"local-{uuid.uuid4()}"


def test_create_patch_get_post_chain(playground):
    """POST создаёт пост, PATCH меняет title, GET подтверждает результат."""
    payload = {
        "title": "Lab2 chain post",
        "body": "Created by pytest REST scenario",
        "user_id": 1,
    }

    created = playground.post("/posts", json=payload)
    assert created.status_code == 201, f"ожидали 201, получили {created.status_code}: {created.text}"
    created_json = created.json()
    post_id = created_json["id"]
    assert post_id, "id созданного поста пуст"
    assert created_json["title"] == payload["title"]
    assert created_json["body"] == payload["body"]

    patched = playground.patch(f"/posts/{post_id}", json={"title": NEW_TITLE})
    assert patched.status_code == 200, patched.text
    patched_json = patched.json()
    assert patched_json["title"] == NEW_TITLE, "title не изменился после PATCH"
    assert patched_json["body"] == payload["body"], "PATCH затронул body, хотя не должен был"

    fetched = playground.get(f"/posts/{post_id}")
    assert fetched.status_code == 200, fetched.text
    fetched_json = fetched.json()
    assert str(fetched_json["id"]) == str(post_id), "GET вернул другой id"
    assert fetched_json["title"] == NEW_TITLE, "изменение title не сохранилось"
    assert fetched_json["body"] == payload["body"], "body не сохранился после PATCH"
    assert fetched_json["user_id"] == payload["user_id"], "user_id не сохранился после PATCH"


@pytest.mark.parametrize(
    "method, path_template",
    [
        pytest.param("GET", "/posts/{post_id}", id="get-missing-post"),
        pytest.param("PATCH", "/posts/{post_id}", id="patch-missing-post"),
    ],
)
def test_missing_post_returns_404(playground, method, path_template):
    """GET/PATCH несуществующего post id ожидают 404 (дополнительный негатив)."""
    path = path_template.format(post_id=MISSING_POST_ID)
    if method == "GET":
        response = playground.get(path)
    else:
        response = playground.patch(path, json={"title": "must not be applied"})

    assert response.status_code == 404, (
        f"{method} несуществующего поста: ожидали 404, получили {response.status_code}: {response.text}"
    )
    body = response.json()
    assert body.get("status") == 404 or "not" in body.get("message", "").lower(), (
        f"тело ошибки не описывает отсутствие ресурса: {body}"
    )

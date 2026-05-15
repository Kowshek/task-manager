"""Tests for task CRUD endpoints."""


class TestCreateTask:
    def test_create_task_success(self, client, auth_headers):
        res = client.post("/tasks", json={"title": "Buy milk"}, headers=auth_headers)
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Buy milk"
        assert data["completed"] is False
        assert "id" in data

    def test_create_task_with_description(self, client, auth_headers):
        res = client.post("/tasks", json={
            "title": "Go shopping",
            "description": "Milk, eggs, bread",
        }, headers=auth_headers)
        assert res.status_code == 201
        assert res.json()["description"] == "Milk, eggs, bread"

    def test_create_task_requires_auth(self, client):
        res = client.post("/tasks", json={"title": "No auth task"})
        assert res.status_code == 401

    def test_create_task_empty_title_fails(self, client, auth_headers):
        res = client.post("/tasks", json={"title": ""}, headers=auth_headers)
        assert res.status_code == 422


class TestListTasks:
    def test_list_tasks_empty(self, client, auth_headers):
        res = client.get("/tasks", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 0
        assert data["tasks"] == []

    def test_list_tasks_returns_own_tasks_only(self, client, auth_headers):
        # Create task for user 1
        client.post("/tasks", json={"title": "User1 task"}, headers=auth_headers)

        # Register and login as user 2
        client.post("/register", json={"username": "user2", "email": "u2@test.com", "password": "pass123"})
        login = client.post("/login", json={"username": "user2", "password": "pass123"})
        headers2 = {"Authorization": f"Bearer {login.json()['access_token']}"}

        res = client.get("/tasks", headers=headers2)
        assert res.json()["total"] == 0  # user2 sees zero tasks

    def test_list_tasks_pagination(self, client, auth_headers):
        for i in range(7):
            client.post("/tasks", json={"title": f"Task {i}"}, headers=auth_headers)

        res = client.get("/tasks?page=1&limit=5", headers=auth_headers)
        data = res.json()
        assert data["total"] == 7
        assert len(data["tasks"]) == 5
        assert data["page"] == 1

        res2 = client.get("/tasks?page=2&limit=5", headers=auth_headers)
        assert len(res2.json()["tasks"]) == 2

    def test_list_tasks_filter_completed(self, client, auth_headers):
        res1 = client.post("/tasks", json={"title": "Task A"}, headers=auth_headers)
        task_id = res1.json()["id"]
        client.post("/tasks", json={"title": "Task B"}, headers=auth_headers)

        # Mark one complete
        client.put(f"/tasks/{task_id}", json={"completed": True}, headers=auth_headers)

        completed = client.get("/tasks?completed=true", headers=auth_headers).json()
        pending   = client.get("/tasks?completed=false", headers=auth_headers).json()

        assert completed["total"] == 1
        assert pending["total"] == 1


class TestGetTask:
    def test_get_task_success(self, client, auth_headers):
        created = client.post("/tasks", json={"title": "Find me"}, headers=auth_headers).json()
        res = client.get(f"/tasks/{created['id']}", headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["title"] == "Find me"

    def test_get_task_not_found(self, client, auth_headers):
        res = client.get("/tasks/9999", headers=auth_headers)
        assert res.status_code == 404

    def test_get_task_other_user_forbidden(self, client, auth_headers):
        created = client.post("/tasks", json={"title": "Mine"}, headers=auth_headers).json()

        client.post("/register", json={"username": "user2", "email": "u2@test.com", "password": "pass123"})
        login = client.post("/login", json={"username": "user2", "password": "pass123"})
        headers2 = {"Authorization": f"Bearer {login.json()['access_token']}"}

        res = client.get(f"/tasks/{created['id']}", headers=headers2)
        assert res.status_code == 404  # looks like "not found" to other users


class TestUpdateTask:
    def test_mark_task_completed(self, client, auth_headers):
        task = client.post("/tasks", json={"title": "Do thing"}, headers=auth_headers).json()
        res = client.put(f"/tasks/{task['id']}", json={"completed": True}, headers=auth_headers)
        assert res.status_code == 200
        assert res.json()["completed"] is True

    def test_update_title(self, client, auth_headers):
        task = client.post("/tasks", json={"title": "Old title"}, headers=auth_headers).json()
        res = client.put(f"/tasks/{task['id']}", json={"title": "New title"}, headers=auth_headers)
        assert res.json()["title"] == "New title"

    def test_update_nonexistent_task(self, client, auth_headers):
        res = client.put("/tasks/9999", json={"completed": True}, headers=auth_headers)
        assert res.status_code == 404


class TestDeleteTask:
    def test_delete_task_success(self, client, auth_headers):
        task = client.post("/tasks", json={"title": "Delete me"}, headers=auth_headers).json()
        res = client.delete(f"/tasks/{task['id']}", headers=auth_headers)
        assert res.status_code == 204

        # Confirm it's gone
        get_res = client.get(f"/tasks/{task['id']}", headers=auth_headers)
        assert get_res.status_code == 404

    def test_delete_nonexistent_task(self, client, auth_headers):
        res = client.delete("/tasks/9999", headers=auth_headers)
        assert res.status_code == 404

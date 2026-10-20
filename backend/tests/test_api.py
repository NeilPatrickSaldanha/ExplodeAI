from app.config import get_settings

LEARNER = {"X-Learner-Id": "test-learner-0001"}


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_lessons_list_and_detail(client):
    lessons = client.get("/api/lessons").json()
    assert [lesson["id"] for lesson in lessons] [:3] == ["rag-pipeline", "tokenization", "embeddings"]
    detail = client.get("/api/lessons/rag-pipeline").json()
    assert len(detail["components"]) == 8
    cited = {c["source"] for claim in detail["claims"] for c in claim["citations"]}
    assert cited == {s["id"] for s in detail["sources"]}
    assert detail["validation_problems"] == []


def test_draft_lessons_hidden_unless_enabled(client, monkeypatch):
    from app.content import loader
    from app.routers import lessons as lessons_router

    registry, real = loader.content()
    draft = real["rag-pipeline"].model_copy(update={"status": "draft"})
    monkeypatch.setattr(lessons_router, "content", lambda: (registry, {"rag-pipeline": draft}))
    monkeypatch.setattr(get_settings(), "show_draft_lessons", False)
    assert client.get("/api/lessons").json() == []
    assert client.get("/api/lessons/rag-pipeline").status_code == 404
    monkeypatch.setattr(get_settings(), "show_draft_lessons", True)
    assert client.get("/api/lessons/rag-pipeline").status_code == 200


def test_published_lesson_visible_without_draft_flag(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "show_draft_lessons", False)
    from app.content.loader import content

    statuses = [lesson["status"] for lesson in client.get("/api/lessons").json()]
    published = [lesson for lesson in content()[1].values() if lesson.status == "published"]
    assert statuses == ["published"] * len(published) and statuses


def test_experiment_run_persists(client, engine):
    from sqlmodel import Session, select

    from app.db import ExperimentRun

    r = client.post("/api/experiments/rag/run", json={"top_k": 2}, headers=LEARNER)
    assert r.status_code == 200
    assert len(r.json()["retrieved"]) == 2
    with Session(engine) as s:
        runs = s.exec(select(ExperimentRun)).all()
    assert len(runs) == 1 and runs[0].learner_id == "test-learner-0001"


def test_experiment_rejects_bad_params(client):
    assert client.post("/api/experiments/rag/run", json={"chunk_size": 10, "overlap": 10}).status_code == 422
    assert client.post("/api/experiments/rag/run", json={"top_k": 99}).status_code == 422
    assert client.post("/api/experiments/rag/run", json={}, headers={"X-Learner-Id": "bad id!"}).status_code == 400


def test_experiment_config(client):
    cfg = client.get("/api/experiments/rag/config").json()
    assert cfg["stages"][0] == "corpus"
    assert cfg["embedders"][0]["available"] is True


def test_challenge_check_enforces_locked_params(client):
    url = "/api/experiments/rag/challenges/rag-pipeline/ranking-miss/check"
    # Trying to "fix" by raising top_k (locked) is overridden back to 3 → still broken.
    cheat = client.post(url, json={"top_k": 10, "method": "dense"}, headers=LEARNER).json()
    assert cheat["result"]["params"]["top_k"] == 3
    assert not cheat["passed"]
    fixed = client.post(url, json={"method": "hybrid"}, headers=LEARNER).json()
    assert fixed["passed"]


def test_progress_merges_and_filters_unknown_ids(client):
    url = "/api/progress/rag-pipeline"
    assert client.get(url, headers=LEARNER).json()["explored_components"] == []
    client.put(url, json={"explored_components": ["corpus", "nope"]}, headers=LEARNER)
    out = client.put(url, json={"explored_components": ["retriever"],
                                "solved_challenges": ["budget-overflow"],
                                "reconstruction_solved": True}, headers=LEARNER).json()
    assert out["explored_components"] == ["corpus", "retriever"]
    assert out["solved_challenges"] == ["budget-overflow"]
    assert out["reconstruction_solved"] is True
    other = client.get(url, headers={"X-Learner-Id": "someone-else-02"}).json()
    assert other["explored_components"] == []


def test_reconstruction_endpoint(client):
    order = ["corpus", "chunker", "embedder", "vector_index", "query_encoder", "retriever",
             "prompt_builder", "generator"]
    assert client.post("/api/lessons/rag-pipeline/reconstruction/check",
                       json={"order": order}).json()["correct"]

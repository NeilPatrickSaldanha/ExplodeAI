"""Educational content schema.

A lesson is data, not code: components of the exploded view, the claims each
component teaches, the sources behind every claim, and the verification record
for the three passes. `validate_lesson` enforces the publishing rules:

- every claim cites at least one registered source, with a short excerpt;
- every source records URL, access date, and (where it has one) a version;
- a lesson can be `published` only when every claim has passed primary-source
  research, independent cross-check, and technical validation (or the
  technical pass is explicitly not applicable, with a reason);
- every visual declares whether it is a real execution, a simulation, or a
  conceptual diagram.
"""

from datetime import date
from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator

Vec3 = tuple[float, float, float]
PassStatus = Literal["pending", "passed", "failed", "not_applicable"]


class Source(BaseModel):
    id: str
    title: str
    publisher: str
    url: HttpUrl
    type: Literal["paper", "official_docs", "official_blog", "framework_docs", "reference"]
    authors: list[str] = []
    version: str | None = None  # arXiv version, doc "last updated" date, etc.
    published: str | None = None
    accessed: date
    notes: str | None = None


class SourceRegistry(BaseModel):
    sources: list[Source]

    def by_id(self) -> dict[str, Source]:
        return {s.id: s for s in self.sources}


class Citation(BaseModel):
    source: str
    locator: str | None = None  # section, table, page
    excerpt: str

    @field_validator("excerpt")
    @classmethod
    def _short_excerpt(cls, v: str) -> str:
        if len(v.split()) > 30:
            raise ValueError("excerpts must stay short (≤ 30 words) — cite, don't copy")
        return v


class VerificationPass(BaseModel):
    status: PassStatus = "pending"
    date: Date | None = None
    by: str | None = None
    notes: str | None = None


class ClaimVerification(BaseModel):
    primary: VerificationPass = VerificationPass()
    cross_check: VerificationPass = VerificationPass()
    technical: VerificationPass = VerificationPass()


class Claim(BaseModel):
    id: str
    text: str
    kind: Literal["fact", "definition", "provider_specific", "simplification"]
    provider: str | None = None
    citations: list[Citation] = Field(min_length=1)
    verification: ClaimVerification = ClaimVerification()


class Geometry(BaseModel):
    shape: Literal["slab", "stack", "cylinder", "grid", "prism", "lens", "ring", "card"]
    size: Vec3 = (1.0, 1.0, 1.0)


class ExampleDemo(BaseModel):
    """A tiny worked example, shown as input → steps → output. Illustrative, not a claim."""

    input: str
    steps: list[str] = Field(min_length=1)
    output: str


class Explain(BaseModel):
    """Beginner-friendly depth for one stage. Facts restate `claims`; analogies and
    examples are teaching aids and are labelled as such in the UI."""

    what: str
    why: str
    analogy: str
    happens: list[str] = Field(min_length=1)  # what enters, and what is done to it
    goes_to: str
    example: ExampleDemo
    misconfigured: str
    learn_more: str  # optional technical depth, behind a "Learn more" toggle
    claims: list[str] = Field(min_length=1)


class Component(BaseModel):
    id: str
    label: str
    phase: str = Field(min_length=1)  # free-form group, e.g. pipeline phase
    short: str
    detail: str
    claims: list[str] = Field(min_length=1)
    geometry: Geometry
    position: Vec3
    explode: Vec3
    # Optional stage-card content (all optional so other lessons need not set them).
    subtitle: str | None = None  # 2–4 word tagline for the step bar
    icon: str | None = None  # Phosphor icon name
    inputs: list[str] = []
    outputs: list[str] = []
    # What breaks if this stage is removed. Statements here describe THIS
    # lesson's executable pipeline and must be backed by an ablation test.
    breaks_if_removed: str | None = None
    explain: Explain | None = None


class Connection(BaseModel):
    source: str
    target: str
    payload: str
    # Visual flow class: text moving, vectors moving, or the user's question.
    flow: Literal["document", "vector", "query"] | None = None


class Visual(BaseModel):
    id: str
    kind: Literal["real_execution", "simulation", "conceptual"]
    label: str
    description: str


# Which check types each experiment engine can evaluate server-side.
ENGINE_CHECKS: dict[str, set[str]] = {
    "rag": {"gold_in_retrieved", "gold_in_prompt"},
    "tokenize": {"round_trip", "no_unknown", "max_tokens", "single_token", "no_cross_word_tokens"},
    "embed": {"top1_category", "comparable"},
    "attend": {"no_future_attention", "not_saturated", "order_matters"},
    "agent": {"stops_within", "answer_contains", "no_unapproved_side_effects"},
}


class Check(BaseModel):
    type: Literal[
        "gold_in_retrieved", "gold_in_prompt",  # rag
        "round_trip", "no_unknown", "max_tokens", "single_token", "no_cross_word_tokens",  # tokenize
        "top1_category", "comparable",  # embed
        "no_future_attention", "not_saturated", "order_matters",  # attend
        "stops_within", "answer_contains", "no_unapproved_side_effects",  # agent
    ]
    gold: list[str] = []
    limit: int | None = None

    @model_validator(mode="after")
    def _needs_operands(self):
        needs_gold = (
            "gold_in_retrieved", "gold_in_prompt", "single_token", "top1_category", "answer_contains",
        )
        if self.type in needs_gold and not self.gold:
            raise ValueError(f"{self.type} checks need at least one gold string")
        if self.type in ("max_tokens", "not_saturated", "stops_within") and self.limit is None:
            raise ValueError(f"{self.type} checks need a limit")
        return self


class Challenge(BaseModel):
    id: str
    title: str
    brief: str
    broken_params: dict
    locked_params: list[str] = []
    checks: list[Check] = Field(min_length=1)
    hint: str
    explanation: str
    claims: list[str] = []


class Reconstruction(BaseModel):
    prompt: str
    dependencies: dict[str, list[str]]


class TourStep(BaseModel):
    component: str
    title: str
    body: str
    claims: list[str] = []


class Lesson(BaseModel):
    id: str
    number: int = Field(ge=1)  # course order: Lesson 01, 02, …
    title: str
    summary: str
    status: Literal["draft", "published"]
    version: str
    updated: date
    estimated_minutes: int
    objectives: list[str]
    prerequisites: list[str] = []
    claims: list[Claim]
    components: list[Component]
    connections: list[Connection]
    visuals: list[Visual]
    experiment: dict
    challenges: list[Challenge]
    reconstruction: Reconstruction
    tour: list[TourStep]
    verification_report: str


def validate_lesson(lesson: Lesson, registry: SourceRegistry) -> list[str]:
    """Return a list of human-readable problems. Empty list = valid."""
    problems: list[str] = []
    sources = registry.by_id()
    claim_ids = {c.id for c in lesson.claims}
    component_ids = {c.id for c in lesson.components}

    if len(claim_ids) != len(lesson.claims):
        problems.append("duplicate claim ids")

    for claim in lesson.claims:
        for cit in claim.citations:
            if cit.source not in sources:
                problems.append(f"claim {claim.id}: unknown source '{cit.source}'")
        if claim.kind == "provider_specific" and not claim.provider:
            problems.append(f"claim {claim.id}: provider_specific claims must name the provider")
        v = claim.verification
        for name, p in (("primary", v.primary), ("cross_check", v.cross_check),
                        ("technical", v.technical)):
            if p.status == "failed":
                problems.append(f"claim {claim.id}: {name} pass FAILED — fix before publishing")
            if p.status == "not_applicable" and (name != "technical" or not p.notes):
                problems.append(
                    f"claim {claim.id}: only the technical pass may be not_applicable, "
                    "and it needs a reason in notes"
                )
            if lesson.status == "published" and p.status not in ("passed", "not_applicable"):
                problems.append(f"claim {claim.id}: {name} pass is '{p.status}' in a published lesson")
            if p.status == "passed" and not (p.date and p.by):
                problems.append(f"claim {claim.id}: {name} pass marked passed without date/by")

    referenced = set()
    for comp in lesson.components:
        for cid in comp.claims:
            referenced.add(cid)
            if cid not in claim_ids:
                problems.append(f"component {comp.id}: unknown claim '{cid}'")
    for comp in lesson.components:
        if comp.explain is None:
            problems.append(f"component {comp.id}: no explain section")
            continue
        for cid in comp.explain.claims:
            if cid not in claim_ids:
                problems.append(f"component {comp.id}: explain cites unknown claim '{cid}'")
        if not set(comp.explain.claims) <= set(comp.claims):
            problems.append(f"component {comp.id}: explain claims must be among the component's own claims")
    for ch in lesson.challenges:
        for cid in ch.claims:
            referenced.add(cid)
            if cid not in claim_ids:
                problems.append(f"challenge {ch.id}: unknown claim '{cid}'")
    for step in lesson.tour:
        if step.component not in component_ids:
            problems.append(f"tour step '{step.title}': unknown component '{step.component}'")
        for cid in step.claims:
            referenced.add(cid)
            if cid not in claim_ids:
                problems.append(f"tour step '{step.title}': unknown claim '{cid}'")
    for orphan in sorted(claim_ids - referenced):
        problems.append(f"claim {orphan}: not used by any component, challenge, or tour step")

    for conn in lesson.connections:
        for end in (conn.source, conn.target):
            if end not in component_ids:
                problems.append(f"connection {conn.source}->{conn.target}: unknown component '{end}'")

    engine = lesson.experiment.get("engine")
    allowed = ENGINE_CHECKS.get(engine)
    if allowed is None:
        problems.append(f"experiment: unknown engine '{engine}'")
    else:
        for ch in lesson.challenges:
            for check in ch.checks:
                if check.type not in allowed:
                    problems.append(
                        f"challenge {ch.id}: check '{check.type}' is not available for engine '{engine}'"
                    )

    deps = lesson.reconstruction.dependencies
    if set(deps) != component_ids:
        problems.append("reconstruction dependencies must list exactly the lesson's components")

    for src in sources.values():
        if src.type == "paper" and not src.version:
            problems.append(f"source {src.id}: papers must record the version read")

    return problems

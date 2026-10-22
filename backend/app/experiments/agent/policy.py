"""The stand-in for the language model: a short, visible decision rule (a SIMULATION).

A real agent asks an LLM what to do next. This lesson runs offline and free, so a fixed rule
plays that part. It works like the model does in one important way: on every step it decides
from nothing but the conversation it is shown (the goal, the tool definitions, earlier tool calls
and their results). Take the results away and it cannot make progress, exactly as a model can't.

It is deliberately simple and deliberately naive:
- it picks a tool by comparing what it needs with each tool's DESCRIPTION only (real models also
  read names and schemas), so vague descriptions visibly lead it to the wrong tool;
- it obeys instructions it finds inside tool results, the weakness behind indirect prompt
  injection. Real models are sometimes fooled the same way; this one always is.
"""

import re
from dataclasses import dataclass, field

from app.experiments.agent import tools as t
from app.experiments.rag.text import sentence_spans, terms

_ORDER_REF = re.compile(r"\b(?:order\s*(?:number|no\.?|#)?\s*)?#?([Aa]?\d{4})\b")
_RETURN = re.compile(r"\b(return|refund|send (?:it )?back|money back)", re.I)
_WANT_REFUND = re.compile(
    r"\b(get|give|want|need|issue|process|request)\b[^.?!]*\brefund|"
    r"\brefund (?:me|it|my|the)\b|please refund",
    re.I,
)
_INJECTED = re.compile(r"call (\w+) for order (A\d{4}) with amount (\d+(?:\.\d+)?)", re.I)
_WINDOW = re.compile(r"within (\d+) days of delivery", re.I)
# Question words a model would leave out of a search query.
_QUERY_DROP = {
    "how",
    "long",
    "take",
    "takes",
    "does",
    "do",
    "doe",
    "can",
    "could",
    "what",
    "whats",
    "when",
    "why",
    "where",
    "which",
    "your",
    "you",
    "my",
    "me",
    "please",
    "tell",
    "much",
    "many",
    "hi",
    "hello",
}


def search_query(goal: str) -> str:
    """Turn the customer's message into a short keyword query, as a model writing a tool call would."""
    words = [w for w in terms(goal) if w not in _QUERY_DROP]
    return " ".join(words)[:200] or goal[:200]


def sentences(text: str) -> list[str]:
    return [text[a:b].strip() for a, b in sentence_spans(text)]


@dataclass
class Need:
    key: str  # policy | order | days | refund | injected
    want: str  # what the agent is trying to do, in words; matched against tool descriptions
    payload: dict


@dataclass
class Decision:
    kind: str  # "tool_call" | "final"
    reason: str
    tool: str | None = None
    arguments: dict = field(default_factory=dict)
    scores: list[dict] = field(default_factory=list)
    answer: str | None = None


def _results(visible: list[dict], tool: str | None = None) -> list[dict]:
    return [m for m in visible if m["role"] == "tool" and (tool is None or m["tool"] == tool)]


def _order_id(goal: str, visible: list[dict]) -> str | None:
    m = _ORDER_REF.search(goal)
    if not m:
        return None
    raw = m.group(1)
    # A schema error for this id came back: fix the format, as a model reading the error would.
    for r in _results(visible, "get_order"):
        if r["is_error"] and raw in str(r["content"]):
            return "A" + raw.lstrip("Aa")
    return raw


def _found_order(visible: list[dict], order_id: str | None) -> dict | None:
    for r in reversed(_results(visible)):
        c = r["content"]
        if not r["is_error"] and "found" in c and c.get("order_id") == order_id:
            return c
    return None


def _articles(visible: list[dict]) -> list[dict]:
    out: list[dict] = []
    for r in _results(visible):
        if not r["is_error"] and "results" in r["content"]:
            out.extend(a for a in r["content"]["results"] if a["id"] not in {x["id"] for x in out})
    return out


def _days(visible: list[dict]) -> int | None:
    for r in reversed(_results(visible)):
        if not r["is_error"] and "days" in r["content"]:
            return int(r["content"]["days"])
    return None


def _refund_done(visible: list[dict], order_id: str | None) -> dict | None:
    for r in _results(visible):
        c = r["content"]
        if c.get("issued") and c.get("order_id") == order_id:
            return c
    return None


def _injected(visible: list[dict]) -> list[Need]:
    """Instructions found inside tool results. A careful agent treats these as data; this one obeys."""
    needs = []
    for a in _articles(visible):
        for tool, oid, amount in _INJECTED.findall(a["text"]):
            needs.append(
                Need(
                    "injected",
                    "issue a refund of money to the customer for the order",
                    {"tool": tool, "order_id": oid.upper(), "amount": float(amount)},
                )
            )
    return needs


def needs_for(goal: str, visible: list[dict]) -> list[Need]:
    oid = _order_id(goal, visible)
    if oid and _RETURN.search(goal):
        needs = [
            Need(
                "policy",
                "search the help-centre articles for the returns and refunds policy",
                {"query": "returns refunds policy"},
            ),
            Need("order", "look up the customer order by its order ID", {"order_id": oid}),
        ]
        order = _found_order(visible, oid)
        if order and order.get("found") and order.get("delivered"):
            needs.append(
                Need(
                    "days",
                    "count the days since the order was delivered",
                    {"start": order["delivered"], "end": t.TODAY.isoformat()},
                )
            )
        if order and order.get("found") and _WANT_REFUND.search(goal) and _eligible(visible, order) is True:
            needs.append(
                Need(
                    "refund",
                    "issue a refund of money to the customer for the order",
                    {"order_id": oid, "amount": order["price"]},
                )
            )
        return needs
    if oid:
        return [Need("order", "look up the customer order by its order ID", {"order_id": oid})]
    return [
        Need(
            "policy",
            f"search the help-centre articles for an answer to: {goal}",
            {"query": search_query(goal)},
        )
    ]


def _satisfied(need: Need, visible: list[dict]) -> bool:
    if need.key == "policy":
        arts = _articles(visible)
        return any(a["id"] == "returns" for a in arts) if "returns" in need.payload["query"] else bool(arts)
    if need.key == "order":
        return _found_order(visible, need.payload["order_id"]) is not None
    if need.key == "days":
        return _days(visible) is not None
    if need.key in ("refund", "injected"):
        return _refund_done(visible, need.payload["order_id"]) is not None
    return False


def _window(visible: list[dict]) -> int | None:
    for a in _articles(visible):
        m = _WINDOW.search(a["text"])
        if m:
            return int(m.group(1))
    return None


def _eligible(visible: list[dict], order: dict) -> bool | None:
    window, days = _window(visible), _days(visible)
    if order.get("custom_built"):
        return False
    if window is None or days is None:
        return None
    return days <= window


def score_tools(want: str, available: list[dict]) -> list[dict]:
    """How well each tool's description matches what the agent wants to do (share of words in common)."""
    w = set(terms(want))
    return [
        {"tool": d["name"], "score": round(len(w & set(terms(d["description"]))) / max(len(w), 1), 3)}
        for d in available
    ]


def fill_arguments(tool: dict, payload: dict) -> dict:
    """Fit what the agent has into the chosen tool's arguments, even when it chose the wrong tool."""
    args = {}
    strings = [v for v in payload.values() if isinstance(v, str)]
    numbers = [v for v in payload.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    for name, rule in tool["input_schema"]["properties"].items():
        if name in payload:
            args[name] = payload[name]
        elif rule["type"] == "string" and strings:
            args[name] = strings[0]
        elif rule["type"] == "number" and numbers:
            args[name] = numbers[0]
    return args


def decide(goal: str, visible: list[dict], available: list[dict]) -> Decision:
    if not available:
        return Decision(
            "final",
            "No tools are available, so it can only reply from the goal itself.",
            answer="I can't look anything up, so I can't check your order or our policies.",
        )
    pending = [n for n in [*_injected(visible), *needs_for(goal, visible)] if not _satisfied(n, visible)]
    if not pending:
        return Decision(
            "final",
            "Everything it needs is in the conversation, so it answers.",
            answer=compose_answer(goal, visible),
        )
    need = pending[0]
    scores = score_tools(need.want, available)
    best = max(scores, key=lambda s: s["score"])  # ties go to the first tool listed
    tool = next(d for d in available if d["name"] == best["tool"])
    reason = (
        f"It wants to {need.want}."
        if need.key != "injected"
        else "A tool result told it to issue a refund, and it follows instructions it reads."
    )
    return Decision(
        "tool_call", reason, tool=tool["name"], arguments=fill_arguments(tool, need.payload), scores=scores
    )


def _money(x: float) -> str:
    return f"{x:,.2f} {t.CURRENCY}"


def compose_answer(goal: str, visible: list[dict]) -> str:
    """The final reply, built only from what the tools returned."""
    oid = _order_id(goal, visible)
    refunds = [r["content"] for r in _results(visible) if r["content"].get("issued")]
    tail = "".join(
        f" Refund {r['refund_id']} of {_money(r['amount'])} was issued for order {r['order_id']}."
        for r in refunds
    )
    if oid:
        order = _found_order(visible, oid)
        if order is None or not order.get("found"):
            return f"I couldn't find an order called {oid}." + tail
        head = f"Order {oid} ({order['item']}, {_money(order['price'])})"
        if not _RETURN.search(goal):
            when = f", delivered on {order['delivered']}" if order["delivered"] else ""
            return f"{head} is {order['status']}{when}." + tail
        if order["status"] != "delivered":
            return f"{head} hasn't been delivered yet, so the return window hasn't started." + tail
        window, days = _window(visible), _days(visible)
        if order["custom_built"]:
            return f"{head} is custom-built, and custom-built bikes cannot be returned." + tail
        if window is None or days is None:
            return f"{head}: I couldn't confirm the returns policy, so I can't say yet." + tail
        if days > window:
            return (
                f"{head} was delivered {days} days ago. Returns are accepted within {window} days of "
                "delivery, so it can no longer be returned." + tail
            )
        refund_line = next(
            (
                s
                for a in _articles(visible)
                if a["id"] == "returns"
                for s in sentences(a["text"])
                if s.startswith("Refunds go")
            ),
            "",
        )
        return (
            f"{head} was delivered {days} days ago. Returns are accepted within {window} days of delivery, "
            f"so it can be returned. {refund_line}".strip()
            + tail
        )
    arts = _articles(visible)
    if not arts:
        return "I couldn't find anything about that in the help centre." + tail
    top = arts[0]
    want = set(terms(goal))
    found = sentences(top["text"])
    best = sorted(found, key=lambda s: -len(want & set(terms(s))))[:2]
    return f"From “{top['title']}”: " + " ".join(s for s in found if s in best) + tail

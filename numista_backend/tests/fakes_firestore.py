"""In-memory Firestore fake for the v2 transfer / allowance / sold tests (PLAN v1.2).

Differences from the fake in test_transfer.py: set(merge=True) understands Increment and
DELETE_FIELD (needed by the claim limiter), collections support where(field, '==', value),
and a collection can be told to fail (limiter fail-closed test) or to forbid deletes.
"""
import uuid

from google.cloud import firestore


class Snap:
    def __init__(self, doc_id, data, exists=True, reference=None):
        self.reference = reference
        self.id = doc_id
        self._data = dict(data) if data is not None else None
        self.exists = exists

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


def _apply(target: dict, data: dict):
    for k, v in data.items():
        if v == firestore.DELETE_FIELD:
            target.pop(k, None)
        elif isinstance(v, firestore.Increment):
            target[k] = int(target.get(k, 0)) + int(v.value)
        else:
            target[k] = v


class Ref:
    def __init__(self, db, doc_id, path):
        self.db, self.id, self.path = db, doc_id, path

    def _check(self, op):
        for prefix in self.db.fail_prefixes:
            if self.path.startswith(prefix):
                raise RuntimeError(f"forced failure on {op} {self.path}")

    def get(self, transaction=None):
        self._check("get")
        if self.path in self.db.store:
            return Snap(self.id, self.db.store[self.path], reference=self)
        return Snap(self.id, None, exists=False)

    def set(self, data, merge=False):
        self._check("set")
        if merge and self.path in self.db.store:
            _apply(self.db.store[self.path], data)
        else:
            new = {}
            _apply(new, data)
            self.db.store[self.path] = new

    def update(self, data):
        self._check("update")
        if self.path not in self.db.store:
            raise ValueError(f"Document {self.path} does not exist to update")
        _apply(self.db.store[self.path], data)

    def delete(self):
        self._check("delete")
        for prefix in self.db.no_delete_prefixes:
            if self.path.startswith(prefix):
                raise AssertionError(f"delete forbidden on {self.path}")
        self.db.store.pop(self.path, None)

    def collection(self, name):
        return Col(self.db, f"{self.path}/{name}")


class Col:
    def __init__(self, db, path, filters=()):
        self.db, self.path, self.filters = db, path, tuple(filters)

    def document(self, doc_id=None):
        doc_id = doc_id or uuid.uuid4().hex[:12]
        return Ref(self.db, doc_id, f"{self.path}/{doc_id}")

    def where(self, field, op, value):
        assert op == "==", "fake only supports =="
        return Col(self.db, self.path, self.filters + ((field, value),))

    def stream(self):
        prefix = f"{self.path}/"
        for p, d in list(self.db.store.items()):
            if p.startswith(prefix) and "/" not in p[len(prefix):]:
                if all(d.get(f) == v for f, v in self.filters):
                    yield Snap(p[len(prefix):], d, reference=Ref(self.db, p[len(prefix):], p))

    def get(self):
        return list(self.stream())

    def add(self, data):
        ref = self.document()
        ref.set(data)
        return None, ref


class Txn:
    def get(self, ref):
        return ref.get()

    def update(self, ref, data):
        ref.update(data)

    def set(self, ref, data, merge=False):
        ref.set(data, merge=merge)

    def delete(self, ref):
        ref.delete()


class Batch:
    def __init__(self):
        self.ops = []

    def set(self, ref, data, merge=False):
        self.ops.append(("set", ref, data, merge))

    def update(self, ref, data):
        self.ops.append(("update", ref, data))

    def delete(self, ref):
        self.ops.append(("delete", ref))

    def commit(self):
        for op in self.ops:
            if op[0] == "set":
                op[1].set(op[2], merge=op[3])
            elif op[0] == "update":
                op[1].update(op[2])
            else:
                op[1].delete()
        self.ops.clear()


class FakeDB:
    def __init__(self):
        self.store = {}
        self.fail_prefixes = []       # any op on a path under these prefixes raises
        self.no_delete_prefixes = []  # deleting under these prefixes raises AssertionError

    def collection(self, name):
        return Col(self, name)

    def transaction(self):
        return Txn()

    def batch(self):
        return Batch()


def seed_item(db, user, item_id, subcol="coins", **fields):
    data = {"Year": "1921", "Denomination": "Dollar", "Program/Series": "Morgan Silver Dollar",
            "Mint Mark": "S", "Quantity": 1, "is_demo": False, "is_demo_cleared": False,
            "created_at": "2026-01-01T00:00:00+00:00", "transferStatus": "none"}
    data.update(fields)
    db.store[f"users/{user}/{subcol}/{item_id}"] = data
    return data


def item(db, user, item_id, subcol="coins"):
    return db.store.get(f"users/{user}/{subcol}/{item_id}")

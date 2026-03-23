from typing import Sequence, Union

import importlib
import os
import sys

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b0c0000001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _load_all_model_modules() -> None:
    _here = os.path.dirname(os.path.abspath(__file__))
    _backend = os.path.dirname(os.path.dirname(_here))
    if _backend not in sys.path:
        sys.path.insert(0, _backend)
    _models_dir = os.path.join(_backend, "app", "models")
    if not os.path.isdir(_models_dir):
        return
    for _fn in sorted(os.listdir(_models_dir)):
        if not _fn.endswith(".py") or _fn.startswith("_"):
            continue
        _mod = f"app.models.{_fn[:-3]}"
        try:
            importlib.import_module(_mod)
        except Exception as exc:  # noqa: BLE001
            print(f"WARN: baseline migration skipped { _mod }: {exc}", file=sys.stderr)


def upgrade() -> None:
    """Create all tables from Base.metadata."""
    from app.core.database import Base

    _load_all_model_modules()
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Baseline is not reversed; drop the database or schema if you need a clean slate."""
    pass

from __future__ import annotations

import uvicorn

from mock_netsuite.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run("mock_netsuite.app:app", host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()

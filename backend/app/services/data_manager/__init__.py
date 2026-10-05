"""Decomposition home for the ``data_manager_v2.py`` god-file (BR1.4).

Each extracted responsibility lives in its own sub-package under this package,
mirroring the proven DDD shape already used by ``analytics/`` and ``sync/*``:

- ``<resp>/domain/ports.py``            — consumer-owned ``typing.Protocol``;
                                          no SQL, no framework (BR1.3).
- ``<resp>/application/<resp>.py``      — orchestrator/logic over the port;
                                          no SQL (BR1.3).
- ``<resp>/infrastructure/<resp>_adapter.py`` — the only module with SQL,
                                          wrapping the former god-file SQL
                                          verbatim incl. the engine branch
                                          (BR1.2/FR1.4).

The ``DataManagerV2`` facade keeps every public method name and signature
byte-for-byte (BR1.1); its method bodies are thinned to delegate here. No method
is ever added to the facade (BR1.4).
"""

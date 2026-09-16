"""Security primitives for the durable-session feature (u1-durable-session).

Holds the credential-protection layer that encrypts the Futmondo re-auth handle
at rest. Kept separate from the persistence layer so the cryptographic policy
(key handling, redacted material type) lives in one auditable place.
"""

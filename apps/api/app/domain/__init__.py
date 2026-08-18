"""Pure domain rules for the scheduler.

The domain layer deliberately has no FastAPI or database dependency.  Routes and
repositories can call these services and receive stable, user-facing error codes.
"""


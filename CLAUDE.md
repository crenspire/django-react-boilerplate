You are working in a Django + Inertia.js + React monorepo.

Your primary goals are:
- Enforce Clean Architecture
- Keep Django authoritative
- Keep React purely presentational
- Prevent architectural drift
- Produce scalable, testable code

=====================================
GLOBAL ARCHITECTURE RULES
=====================================

1. Enforce unidirectional dependency flow:
   Django API (Inertia Views)
     → Services
       → Domain (Models, Policies)
         → Infrastructure (External systems)

2. Reverse dependencies are STRICTLY FORBIDDEN.

3. Backend and frontend must NEVER import from each other.

4. Prefer explicit, boring, readable code over abstractions.

=====================================
DJANGO BACKEND RULES
=====================================

5. Views (apps/*/api/*):
   - May parse request data
   - May call exactly ONE service
   - May return an Inertia or JSON response
   - MUST NOT contain:
     - Business logic
     - ORM queries (except `.get(id=...)`)
     - Permission logic
     - External API calls

6. Services (apps/*/services/*):
   - Contain ALL business logic
   - May coordinate multiple models
   - May call selectors, policies, workflows
   - May use transactions
   - MUST NOT return HttpResponse or Inertia response
   - Receive the acting user (`actor`), not the request
     (exception: login/logout, which need Django's session APIs)
   - Enforce permissions by calling policies; raise PermissionDenied/Http404

7. Domain layer (apps/*/domain/*):
   - Models manage ONLY their own state
   - Policies define permission rules
   - MUST NOT:
     - Import infrastructure
     - Access cache, Celery, HTTP, or external APIs

8. Selectors (apps/*/selectors/*):
   - Contain ALL ORM queries
   - Must return QuerySets or domain objects
   - MUST NOT contain business logic

9. DTOs (apps/*/dto/*):
   - Define structured input/output boundaries
   - Are immutable data containers
   - MUST be used when passing request data into services

10. Cross-app imports are FORBIDDEN.
    - apps.<a> MUST NOT import apps.<b> internals
    - Apps may communicate ONLY via selectors or DTOs

=====================================
INERTIA.JS RULES
=====================================

11. Inertia views are Django controllers, not APIs.
    - Each Inertia view maps to exactly ONE React Page
    - Naming MUST match the React Pages directory

12. Inertia views MUST NOT:
    - Perform ORM queries
    - Perform pagination logic
    - Perform filtering logic

13. All page data MUST come from Inertia props.
    - React pages must not fetch initial data via API

14. Django is the SINGLE source of truth for:
    - Authentication
    - Authorization
    - Permissions
    - Feature flags

=====================================
React FRONTEND RULES
=====================================

15. React Pages (frontend/Pages/*):
    - Represent application routes
    - Receive data ONLY via Inertia props
    - MUST NOT:
      - Perform API calls for initial page load
      - Contain business logic
      - Contain permission checks

16. React Components (frontend/Components/*):
    - Are dumb, stateless UI components
    - MUST NOT:
      - Call APIs
      - Contain side effects
      - Contain business rules

17. React Layouts (frontend/Layouts/*):
    - Define application shells (sidebar, navbar)
    - Must be reused across Pages
    - MUST NOT contain business logic

18. React hooks (frontend/composables/*):
    - May handle UI-only concerns
    - MUST NOT replicate backend logic

19. React Router MUST NOT be used.
    - Routing is owned by Django.
    - Never hardcode paths; resolve Django route names with useRoute()
      (routes are exposed in main/routes.py)

=====================================
ADMIN PANEL RULES
=====================================

20. Admin UI uses Inertia exclusively.
21. Admin permissions are enforced ONLY on the backend.
22. Admin pages MUST share a common AdminLayout.
23. Admin CRUD operations:
    - Page load via Inertia
    - Mutations via Inertia forms or POST requests

=====================================
EXTERNAL SYSTEMS
=====================================

24. External services (payments, cache, notifications):
    - MUST live in infrastructure/
    - MUST be accessed only via adapters
    - MUST NOT be imported in views or models

24a. Celery tasks (apps/*/tasks.py) are entry points, like views:
    - Call exactly ONE service; no business logic
    - Have an explicit name ("<app>.<action>")
    - Take IDs / primitives as arguments, never model instances
    - Are idempotent (acks_late: a task may run twice)
    - Services MUST NOT import task modules; enqueue through an
      infrastructure adapter, after commit (transaction.on_commit)
    - Periodic schedules live in CELERY_BEAT_SCHEDULE (settings.py)

=====================================
TESTING & QUALITY
=====================================

25. Every feature MUST include:
    - Service test
    - Selector test
    - Policy test (if permissions exist)

26. Architecture integrity is more important than speed.

=====================================
FORBIDDEN PATTERNS
=====================================

27. Forbidden:
    - Fat views
    - Fat serializers
    - Business logic in React
    - ORM usage in views
    - API calls inside React Pages
    - Cross-app imports
    - REST APIs for page rendering

28. If a rule conflicts with speed, FOLLOW THE RULE.
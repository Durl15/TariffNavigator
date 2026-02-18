"""
Quick verification script to check admin panel setup.
Run this to verify all components are properly configured.
"""
import sys

def check_imports():
    """Verify all required imports work."""
    print("Checking imports...")
    try:
        from app.middleware.audit import AuditMiddleware, log_audit
        print("  [OK] Middleware imports")

        from app.api.endpoints import admin
        print(f"  [OK] Admin endpoints ({len(admin.router.routes)} routes)")

        from app.schemas.admin import (
            UserCreate, UserUpdate, UserResponse, UserListResponse,
            OrganizationCreate, OrganizationUpdate, OrganizationResponse,
            SystemStats, AuditLogResponse
        )
        print("  [OK] Admin schemas")

        from app.api.deps import get_current_admin_user, get_current_superuser
        print("  [OK] Auth dependencies")

        from app.models.user import User
        from app.models.organization import Organization
        from app.models.calculation import Calculation, AuditLog, SharedLink
        print("  [OK] Database models")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def check_routes():
    """List all admin routes."""
    print("\nAdmin routes:")
    try:
        from app.api.endpoints import admin

        routes = [
            (route.methods, route.path, route.name)
            for route in admin.router.routes
            if hasattr(route, 'methods')
        ]

        for methods, path, name in sorted(routes, key=lambda x: x[1]):
            method_str = ','.join(methods)
            print(f"  {method_str:8} {path:40} ({name})")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def check_app_config():
    """Verify main app configuration."""
    print("\nApplication configuration:")
    try:
        import main

        # Check middleware
        middleware_names = [m.__class__.__name__ for m in main.app.user_middleware]
        print(f"  Middleware: {', '.join(middleware_names)}")

        # Check if admin router is registered
        all_routes = [route.path for route in main.app.routes if hasattr(route, 'path')]
        admin_routes = [r for r in all_routes if '/admin' in r]
        print(f"  Admin routes registered: {len(admin_routes)}")

        return True
    except Exception as e:
        print(f"  [FAIL] {e}")
        return False


def main_check():
    """Run all verification checks."""
    print("=" * 60)
    print("Admin Panel Setup Verification")
    print("=" * 60)

    checks = [
        ("Imports", check_imports),
        ("Routes", check_routes),
        ("App Config", check_app_config)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            results.append((name, False))

    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)

    all_passed = all(result for _, result in results)

    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")

    print("\n" + "=" * 60)

    if all_passed:
        print("\nAll checks passed! Admin panel is ready to use.")
        print("\nNext steps:")
        print("  1. Run migrations: alembic upgrade head")
        print("  2. Create admin user: python scripts/create_admin_user.py")
        print("  3. Start server: uvicorn main:app --reload")
        print("  4. Test endpoints with curl or Postman")
        return 0
    else:
        print("\nSome checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main_check())

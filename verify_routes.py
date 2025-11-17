#!/usr/bin/env python3
"""Simple script to verify routes are registered correctly"""

from app.main import app

print("=" * 60)
print("CodeShield AI Backend - Route Verification")
print("=" * 60)
print("\nAvailable Routes:\n")

for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        methods = ', '.join(route.methods) if route.methods else 'N/A'
        print(f"  {methods:10} {route.path}")

print("\n" + "=" * 60)
print("Total routes:", len([r for r in app.routes if hasattr(r, 'path')]))
print("=" * 60)


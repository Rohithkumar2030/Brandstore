#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'greatkart.settings')
    try:
        import django
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # Guard against Python/Django combinations known to fail in admin template rendering.
    if sys.version_info >= (3, 14) and django.VERSION < (5, 2):
        raise RuntimeError(
            "Incompatible runtime detected: Python 3.14 requires Django >= 5.2 for stable admin rendering. "
            "Upgrade Django in your active environment (pip install 'Django>=5.2.8,<7.0') "
            "or use the project's virtual environment."
        )

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

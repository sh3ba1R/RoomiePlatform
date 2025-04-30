#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RoomiePlatform.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Handle port permission errors for runserver command
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver' and len(sys.argv) <= 2:
        # No port specified, try with an alternative port
        try:
            execute_from_command_line(sys.argv)
        except PermissionError:
            print("Permission error on default port. Trying alternative port 8080...")
            sys.argv.append('8080')
            execute_from_command_line(sys.argv)
    else:
        execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

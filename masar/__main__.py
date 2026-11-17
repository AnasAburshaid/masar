"""Package executable entry point for python -m masar."""

import sys
from masar.presentation.cli import main

if __name__ == "__main__":
    sys.exit(main())

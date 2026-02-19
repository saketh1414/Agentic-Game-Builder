"""
Main entry point for the Agentic Game Builder.

Usage:
    python main.py

Or via Docker:
    docker run -it -v $(pwd)/generated_game:/app/generated_game game-builder
"""
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))

from agents.manager import GameBuilderManager


def main():
    manager = GameBuilderManager()
    try:
        manager.run()
    except KeyboardInterrupt:
        print("\n\nBuild interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        print("Please check your GEMINI_API_KEY and try again.")
        raise


if __name__ == "__main__":
    main()

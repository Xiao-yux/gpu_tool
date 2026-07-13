from core.core import Core


def app() -> None:
    """Entry point for the gpu_tool CLI."""
    c = Core()
    c.run()


if __name__ == '__main__':
    app()
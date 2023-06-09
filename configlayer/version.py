__all__ = "VERSION", "version_info"

VERSION = "0.1.0"

# OPTDEP: Add optional dependencies for your users here, e. g. "devtools", "typing-extensions".
opt_in_dependencies: list[str] = []


def version_info() -> str:
    import platform
    import sys
    from importlib import import_module
    from pathlib import Path

    optional_deps = []
    for p in opt_in_dependencies:
        try:
            import_module(p.replace("-", "_"))
        except ImportError:
            continue
        optional_deps.append(p)

    info = {
        "pydantic version": VERSION,
        "install path": Path(__file__).resolve().parent,
        "python version": sys.version,
        "platform": platform.platform(),
        "optional deps. installed": optional_deps,
    }
    return "\n".join("{:>30} {}".format(k + ":", str(v).replace("\n", " ")) for k, v in info.items())

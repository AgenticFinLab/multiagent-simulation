import io
import os
import re

import setuptools


def get_long_description():
    base_dir = os.path.abspath(os.path.dirname(__file__))
    with io.open(os.path.join(base_dir, "description.txt"), encoding="utf-8") as f:
        return f.read()


def get_requirements(filename: str = "requirements.txt"):
    """Read ``requirements.txt`` as a list of PEP 508 requirement strings.

    ``requirements.txt`` is comment-annotated and section-headered, so the raw
    lines cannot be handed to ``install_requires``: setuptools/pip reject
    comment and blank entries (``InvalidRequirement``), which made
    ``pip install -e .`` fail on a clean checkout. Strip trailing comments and
    blank lines, then de-duplicate while preserving declaration order so a
    package that appears twice cannot silently drift between two specs.
    """
    base_dir = os.path.abspath(os.path.dirname(__file__))
    requirements = []
    seen = set()
    with io.open(os.path.join(base_dir, filename), encoding="utf-8") as f:
        for raw_line in f:
            requirement = raw_line.split("#", 1)[0].strip()
            if not requirement:
                continue
            if requirement in seen:
                continue
            seen.add(requirement)
            requirements.append(requirement)
    return requirements


def get_version():
    current_dir = os.path.abspath(os.path.dirname(__file__))
    version_file = os.path.join(current_dir, "masim", "__init__.py")
    with io.open(version_file, encoding="utf-8") as f:
        return re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', f.read(), re.M).group(1)


setuptools.setup(
    name="multiagent-simulation",
    version=get_version(),
    author="",
    license="Apache-2.0",
    description="Packaged version of financial trend tracer for visual language models",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/AgenticFinLab/multiagent-simulation",
    packages=setuptools.find_packages(exclude=["tests"]),
    python_requires=">=3.11",
    install_requires=get_requirements(),
    extras_require={
        "tests": ["pytest"],
        # Optional heavy stack for the Rag variants (document parsing +
        # embedding/retrieval). The platform core never imports it, so a
        # Rule/LLM user does not have to install llama-index at all.
        "rag": get_requirements("requirements-rag.txt"),
    },
    include_package_data=True,
    options={"bdist_wheel": {"python_tag": "py311"}},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    keywords="multiagent, simulation, large language models",
)

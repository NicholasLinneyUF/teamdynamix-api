import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


def test_built_distributions_include_metadata_and_support_import_smoke(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    build_root = tmp_path / "project"
    build_root.mkdir()

    for filename in ("pyproject.toml", "README.md", "LICENSE", "MANIFEST.in"):
        shutil.copy2(project_root / filename, build_root / filename)
    shutil.copytree(project_root / "src", build_root / "src")

    dist_dir = tmp_path / "dist"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--sdist",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(dist_dir),
        ],
        cwd=build_root,
        check=True,
        capture_output=True,
        text=True,
    )

    wheel = next(dist_dir.glob("*.whl"))
    sdist = next(dist_dir.glob("*.tar.gz"))
    assert "0.0.0a11" in wheel.name

    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = archive.read(metadata_name).decode()
        assert "Version: 0.0.0a11" in metadata
        assert "Requires-Dist: pandas>=2.0" in metadata
        assert "teamdynamix/py.typed" in names
        assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)

    with tarfile.open(sdist) as archive:
        names = archive.getnames()
        assert any(name.endswith("/README.md") for name in names)
        assert any(name.endswith("/LICENSE") for name in names)
        assert any(name.endswith("/src/teamdynamix/py.typed") for name in names)

    subprocess.run(
        [sys.executable, "-m", "twine", "check", str(wheel), str(sdist)],
        check=True,
        capture_output=True,
        text=True,
    )

    target = tmp_path / "installed"
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--target", str(target), str(wheel)],
        check=True,
        capture_output=True,
        text=True,
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = str(target)
    env["PYTHONNOUSERSITE"] = "1"
    subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "from pathlib import Path; "
                "import teamdynamix, teamdynamix.tools; "
                "root = Path(r'" + str(target) + "').resolve(); "
                "assert Path(teamdynamix.__file__).resolve().is_relative_to(root); "
                "assert teamdynamix.__version__ == '0.0.0a11'"
            ),
        ],
        cwd=tmp_path,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

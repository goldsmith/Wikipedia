"""Build first, then exercise wheel and sdist in separate clean environments."""
import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv


def run(*args, cwd=None):
    subprocess.run(list(map(str, args)), cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dist-dir', type=Path, default=Path('dist'))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    artifacts = sorted(args.dist_dir.resolve().glob('wikipedia-*.whl')) + sorted(args.dist_dir.resolve().glob('wikipedia-*.tar.gz'))
    if len(artifacts) != 2:
        raise SystemExit('Expected exactly one wheel and one source distribution')
    scratch = root / 'build'
    scratch.mkdir(exist_ok=True)
    for artifact in artifacts:
        with tempfile.TemporaryDirectory(prefix='installed-test-', dir=scratch) as directory:
            tmp = Path(directory)
            environment = tmp / 'env'
            uv = shutil.which('uv')
            if uv:
                run(uv, 'venv', '--python', sys.executable, environment)
            else:
                venv.EnvBuilder(with_pip=True).create(environment)
            python = environment / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
            requirements = [str(artifact), 'pytest>=8,<10']
            if uv:
                run(uv, 'pip', 'install', '--python', python, *requirements)
            else:
                run(python, '-m', 'pip', 'install', *requirements)
            tests = tmp / 'run'
            tests.mkdir()
            shutil.copytree(root / 'tests', tests / 'tests', ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copyfile(root / 'pytest.ini', tests / 'pytest.ini')
            run(python, '-c',
                "import wikipedia,importlib.metadata,pathlib,sys; "
                "assert pathlib.Path(wikipedia.__file__).is_relative_to(pathlib.Path(sys.prefix)); "
                "assert importlib.metadata.version('wikipedia') == '.'.join(map(str,wikipedia.__version__)); "
                "print('Installed:',wikipedia.__file__,wikipedia.__version__)", cwd=tests)
            run(python, '-m', 'pytest', '-q', cwd=tests)
            print('PASS:', artifact.name, flush=True)


if __name__ == '__main__':
    main()

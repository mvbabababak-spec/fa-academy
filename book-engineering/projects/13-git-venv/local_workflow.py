"""Offline Git and venv exercise in a temporary directory; no network."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys


def git(folder, *args):
    return subprocess.run(['git', *args], cwd=folder, check=True,
                          text=True, capture_output=True).stdout.strip()


def main():
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        repo = root / 'demo'
        repo.mkdir()
        git(repo, 'init', '-q')
        git(repo, 'config', 'user.name', 'Student')
        git(repo, 'config', 'user.email', 'student@example.invalid')
        (repo / '.gitignore').write_text('.venv/\n', encoding='utf-8')
        (repo / 'hello.py').write_text("print('Hello Git')\n", encoding='utf-8')
        subprocess.run([sys.executable, '-m', 'venv', '--without-pip',
                        str(repo / '.venv')], check=True, capture_output=True)
        git(repo, 'add', '.gitignore', 'hello.py')
        git(repo, 'commit', '-qm', 'First practice commit')
        print('commit=', git(repo, 'log', '-1', '--format=%s'))
        print('worktree_clean=', not bool(git(repo, 'status', '--porcelain')))
        print('venv_ignored=', git(repo, 'check-ignore', '.venv'))
        print('network=not used')


if __name__ == '__main__':
    main()

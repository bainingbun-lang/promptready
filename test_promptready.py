import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.dirname(__file__), 'promptready.py')


def correr(d, *args):
    subprocess.run([sys.executable, SCRIPT, d, '-o', os.path.join(d, 'ai_context.txt'), *args], check=True, capture_output=True)
    return open(os.path.join(d, 'ai_context.txt')).read()


def test_filtros():
    with tempfile.TemporaryDirectory() as d:
        for p, c in {'a.py': 'x=1', 'src/b.js': 'y', 'tests/t.py': 'z', 'secreto.txt': 's', 'node_modules/n.js': 'n'}.items():
            os.makedirs(os.path.dirname(os.path.join(d, p)), exist_ok=True)
            open(os.path.join(d, p), 'w').write(c)
        open(os.path.join(d, '.gitignore'), 'w').write('secreto.txt\n')

        t = correr(d)
        assert 'INICIO: a.py' in t and 'INICIO: src/b.js' in t
        assert 'secreto' not in t and 'node_modules' not in t

        t = correr(d, '--exclude', 'tests')
        assert 't.py' not in t and 'a.py' in t

        t = correr(d, '--only', 'src')
        assert 'b.js' in t and 'a.py' not in t


if __name__ == '__main__':
    test_filtros()
    print('ok')

#!/usr/bin/env python3
import argparse
import fnmatch
import os

BASURA = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', '.DS_Store'}
EXT = {'.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.json', '.md', '.txt', '.yml', '.yaml', '.toml', '.sh', '.go', '.rs', '.java', '.c', '.h', '.cpp'}


def leer_gitignore(raiz):
    try:
        with open(os.path.join(raiz, '.gitignore'), encoding='utf-8') as f:
            return [l.strip().rstrip('/') for l in f if l.strip() and not l.startswith(('#', '!'))]
    except OSError:
        return []


def ignorado(rel, nombre, pats):
    # shortcut: no soporta negaciones (!) ni ** completos, usar la lib pathspec si hace falta
    return any(fnmatch.fnmatch(nombre, p) or fnmatch.fnmatch(rel, p.lstrip('/')) for p in pats)


def recorrer(raiz, pats, only, exclude):
    for base, dirs, files in os.walk(raiz):
        rel_base = os.path.relpath(base, raiz)
        dirs[:] = sorted(d for d in dirs if d not in BASURA and not ignorado(os.path.normpath(os.path.join(rel_base, d)), d, pats))
        for f in sorted(files):
            rel = os.path.normpath(os.path.join(rel_base, f))
            partes = rel.split(os.sep)
            if ignorado(rel, f, pats) or os.path.splitext(f)[1] not in EXT:
                continue
            if only and not any(o in partes for o in only):
                continue
            if exclude and any(e in partes or fnmatch.fnmatch(f, e) for e in exclude):
                continue
            yield rel


def arbol(rutas):
    out, vistos = [], set()
    for r in rutas:
        partes = r.split(os.sep)
        for i, p in enumerate(partes):
            clave = tuple(partes[:i + 1])
            if clave not in vistos:
                vistos.add(clave)
                out.append('    ' * i + p + ('/' if i < len(partes) - 1 else ''))
    return '\n'.join(out)


def main():
    ap = argparse.ArgumentParser(prog='promptready', description='Empaqueta un repo en un .txt listo para pegar en una IA')
    ap.add_argument('ruta', nargs='?', default='.')
    ap.add_argument('-o', '--output', default='ai_context.txt')
    ap.add_argument('--only', nargs='+', default=[], help='solo estas carpetas/archivos')
    ap.add_argument('--exclude', nargs='+', default=[], help='saltar estas carpetas/patrones')
    ap.add_argument('--max-tokens', type=int, default=100000)
    a = ap.parse_args()

    raiz = os.path.abspath(a.ruta)
    salida = os.path.abspath(a.output)
    pats = leer_gitignore(raiz)
    rutas = [r for r in recorrer(raiz, pats, a.only, a.exclude) if os.path.abspath(os.path.join(raiz, r)) != salida]

    partes = ['# ESTRUCTURA DEL PROYECTO\n\n' + arbol(rutas) + '\n\n# CONTENIDO DE LOS ARCHIVOS\n']
    for r in rutas:
        try:
            with open(os.path.join(raiz, r), encoding='utf-8') as f:
                cuerpo = f.read()
        except (OSError, UnicodeDecodeError) as e:
            cuerpo = f'[no se pudo leer: {e}]\n'
        partes.append(f'\n--- INICIO: {r} ---\n{cuerpo}\n--- FIN: {r} ---\n')
    texto = ''.join(partes)

    with open(salida, 'w', encoding='utf-8') as f:
        f.write(texto)

    n = len(texto) // 4  # ~4 caracteres por token
    print(f'{len(rutas)} archivos, ~{n:,} tokens -> {a.output}')
    if n > a.max_tokens:
        print(f'aviso: pasa de {a.max_tokens:,} tokens, usa --only o --exclude para recortar')


if __name__ == '__main__':
    main()

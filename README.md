# promptready

![demo](demo.gif)

Un comando y todo tu repo queda en un solo `.txt` limpio, con el árbol del proyecto y el conteo de tokens, listo para pegar en ChatGPT, Claude o Gemini.

```
$ promptready
42 archivos, ~18,310 tokens -> ai_context.txt
```

## Instalar

```
pipx install promptready
```

Sin dependencias, sin APIs, corre en local en milisegundos.

## Uso

```
promptready                          # el directorio actual
promptready ../mi-app -o ctx.txt
promptready --only src components    # solo esas carpetas
promptready --exclude tests docs     # saltar carpetas o patrones (*.test.js)
promptready --max-tokens 50000       # avisa si te pasas
```

## Qué hace

- Respeta tu `.gitignore` y salta `node_modules`, `.git`, `venv`, `dist`...
- Pone el árbol de carpetas al principio para que la IA entienda la arquitectura.
- Estima los tokens (~4 caracteres por token) y avisa si el contexto es demasiado grande.

## Límites

- El `.gitignore` no soporta negaciones (`!`) ni `**` completos.
- Los tokens son una estimación, no el conteo exacto de cada modelo.

MIT

from sanic import Sanic
from sanic import response
from html import escape
import json
from urllib.parse import urlencode
from ftfy.fixes import fix_encoding_and_explain


def steps_to_python(s, steps):
    python = ['s = {}'.format(repr(s))]
    lines = []
    has_sloppy = False
    extra_imports = set()
    for method, encoding, _ in steps:
        if method == 'transcode':
            extra_imports.add(encoding)
            line = 's = {}(s)'.format(encoding)
        else:
            if encoding.startswith('sloppy'):
                has_sloppy = True
            line = 's = s.{}({})'.format(method, repr(encoding))
        lines.append(line)
    python = []
    if has_sloppy:
        python.append('import ftfy.bad_codecs  # enables sloppy- codecs')
    for extra in extra_imports:
        python.append('from ftfy.fixes import {}'.format(extra))
    python.append('s = {}'.format(repr(s)))
    return '\n'.join(python + lines + ['print(s)'])


@app.route('/')
async def handle_request(request):
    s = request.args.getlist('s')
    if s:
        s = s[0].strip()
        fixed, steps = fix_encoding_and_explain(s)
        return escape(fixed)
    else:
        return response.html(INDEX.format(
            output='',
            s='',
            steps='',
            examples='\n'.join(examples),
        ))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8006)

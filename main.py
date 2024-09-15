# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import pickle
import base64
import tempfile
import ast


def check_imports(code, allowed_imports):
    tree = ast.parse(code)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in allowed_imports:
                    raise ImportError("Forbidden import: %s" % alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module not in allowed_imports:
                raise ImportError("Forbidden import: %s" % node.module)


def execute_python_code(file_path, python_version, encoding='utf-8'):
    if python_version not in (2, 3):
        raise ValueError('Unknown python version to execute code')

    try:
        with open(file_path, 'rb') as file:
            code = file.read().decode('utf-8')
    except IOError:
        return 'File not found: %s' % file_path

    allowed_imports = ('datetime', 'time', 'requests')

    try:
        check_imports(code, allowed_imports)
    except ImportError as e:
        return str(e)

    if 'def main(' not in code:
        return 'Invalid code: missing main function'

    wrapper_code = u"""
import pickle
import base64
import sys


def run_main():
    main_result = main()
    pickled = pickle.dumps(main_result, protocol=2)
    encoded = base64.b64encode(pickled)
    if sys.version_info[0] == 3:
        sys.stdout.buffer.write(encoded)
    else:
        print(encoded)

if __name__ == "__main__":
    run_main()
"""

    full_code = u"# -*- coding: utf-8 -*-\n" + code + u"\n" + wrapper_code

    try:
        python_exec = 'python2' if python_version == 2 else 'python3'

        with tempfile.NamedTemporaryFile(suffix=".py", mode='wb', delete=False) as temp_file:
            temp_file.write(full_code.encode('utf-8'))
            temp_file_path = temp_file.name

        process = subprocess.Popen(
            [python_exec, temp_file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        output, error = process.communicate()

        os.remove(temp_file_path)

        if process.returncode == 0:
            try:
                decoded = base64.b64decode(output)
                if sys.version_info[0] >= 3 and python_version == 2:
                    result = pickle.loads(decoded, encoding='bytes')
                else:
                    result = pickle.loads(decoded)
                return encode_output(result, encoding)
            except Exception as e:
                return "Error decoding output: %s" % str(e)
        return encode_output(error, encoding)
    except Exception as e:
        return 'Error while executing python code: %s' % str(e)


def encode_output(output, encoding):
    return convert_to_bytes(output) if encoding == 'bytes' else convert_to_unicode(output)


def convert_to_bytes(obj):
    if isinstance(obj, (bytes, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, unicode if sys.version_info[0] < 3 else str):
        return obj.encode('utf-8')
    elif isinstance(obj, (list, tuple)):
        return type(obj)(convert_to_bytes(item) for item in obj)
    elif isinstance(obj, dict):
        return {convert_to_bytes(key): convert_to_bytes(value) for key, value in obj.items()}
    elif isinstance(obj, set):
        return {convert_to_bytes(item) for item in obj}
    else:
        return str(obj).encode('utf-8')


def convert_to_unicode(obj):
    if isinstance(obj, (unicode if sys.version_info[0] < 3 else str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    elif isinstance(obj, (list, tuple)):
        return type(obj)(convert_to_unicode(item) for item in obj)
    elif isinstance(obj, dict):
        return {convert_to_unicode(key): convert_to_unicode(value) for key, value in obj.items()}
    elif isinstance(obj, set):
        return {convert_to_unicode(item) for item in obj}
    else:
        return unicode(obj) if sys.version_info[0] < 3 else str(obj)

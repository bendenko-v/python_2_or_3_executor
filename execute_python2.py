from main import execute_python_code
import sys

result = execute_python_code('python2_code.py', 2)

print(result)

if type(result) not in (str, bytes):
    if sys.version_info[0] < 3:
        items = result.iteritems()
    else:
        items = result.items()

    for k, v in items:
        print('> {0}, value: {1}'.format(type(k), type(v)))
        if isinstance(v, dict):
            for k1, v1 in (v.iteritems() if sys.version_info[0] < 3 else v.items()):
                print('  >> {0}, value: {1}'.format(type(k1), type(v1)))
        if isinstance(v, (list, tuple, set)):
            for item in v:
                print('  >> value: {0}'.format(type(item)))

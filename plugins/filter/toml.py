
from ansible.module_utils.six import string_types
from ansible.errors import AnsibleFilterError, AnsibleRuntimeError
from ansible.module_utils._text import to_text
import toml

def load_toml_file(file):
    with open(file, 'r') as f:
        data = toml.load(f)
    return data

def from_toml(toml_file):
    if not isinstance(toml_file, string_types):
        raise AnsibleFilterError('from_toml requires a string, got %s' % type(0))
    return load_toml_file(to_text(toml_file, errors='surrogate_or_strict'))
    
class FilterModule(object):
    def filters(self):
        return {
            'from_toml': from_toml        
        }
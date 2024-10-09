
from ansible.module_utils.six import string_types
from ansible.errors import AnsibleFilterError, AnsibleRuntimeError
from ansible.module_utils._text import to_text

try:
    from ansible.plugins.inventory.toml import toml_loads
except ImportError:
    def toml_loads(v):
        raise AnsibleRuntimeError(
            'Python "toml" or "tomli" library is required.'    
        )
    
def from_toml(o):
    if not isinstance(o, string_types):
        raise AnsibleFilterError('from_toml requires a string, got %s' % type(0))
    return toml_loads(to_text(o, errors='surrogate_or_strict'))
    
class FilterModule(object):
    def filters(self):
        return {
            'from_toml': from_toml        
        }
## This template is based on pdoc's text template with a few tweaks to improve
## the markdown formatting, and to prepare the content ready for splitting into multiple files.
## https://github.com/pdoc3/pdoc/blob/master/pdoc/templates/text.mako

<%!
  def indent(s, spaces=4):
      new = s.replace('\n', '\n' + ' ' * spaces)
      return ' ' * spaces + new.strip()
%>

<%def name="h1(s)"># ${s}
</%def>

<%def name="h2(s)">## ${s}
</%def>

<%def name="h3(s)">### ${s}
</%def>

<%def name="function(func)" buffered="True">
<%
        returns = show_type_annotations and func.return_annotation() or ''
        if returns:
            returns = ' \N{non-breaking hyphen}> ' + returns
%>
```python
def ${func.name}(${", ".join(func.params(annotate=show_type_annotations))})${returns}
```
${func.docstring}
</%def>

<%def name="variable(var)" buffered="True">
<%
        annot = show_type_annotations and var.type_annotation() or ''
        if annot:
            annot = ': ' + annot
%>
* `${var.name}${annot}`
${var.docstring | indent}
</%def>

<%def name="class_(cls)" buffered="True">
```python
class ${cls.name}(${", ".join(cls.params(annotate=show_type_annotations))})
```
${cls.docstring}
<%
  class_vars = cls.class_variables(show_inherited_members, sort=sort_identifiers)
  static_methods = cls.functions(show_inherited_members, sort=sort_identifiers)
  inst_vars = cls.instance_variables(show_inherited_members, sort=sort_identifiers)
  methods = cls.methods(show_inherited_members, sort=sort_identifiers)
  mro = cls.mro()
  subclasses = cls.subclasses()
%>
% if class_vars:
${h2('Class variables')}
% for v in class_vars:
${variable(v)}
% endfor
% endif
% if static_methods:
${h2('Static methods')}
% for f in static_methods:
${function(f)}
% endfor
% endif
% if inst_vars:
${h2('Instance variables')}
% for v in inst_vars:
${variable(v)}
    % endfor
% endif
% if methods:
${h2('Methods')}
% for m in methods:
${h3(f"`{m.name}`")}
${function(m)}
% endfor
% endif
</%def>

## Start the output logic for an entire module.

<%
  variables = module.variables(sort=sort_identifiers)
  classes = module.classes(sort=sort_identifiers)
  functions = module.functions(sort=sort_identifiers)
  submodules = module.submodules()
  heading = 'Namespace' if module.is_namespace else 'Module'
%>

${heading} ${module.name}
=${'=' * (len(module.name) + len(heading))}
${module.docstring}

% if submodules:
Sub-modules
-----------

    % for m in submodules:
* ${m.name}
    % endfor
% endif

% if variables:
Variables
---------

    % for v in variables:
${variable(v)}

    % endfor
% endif

% if functions:
Functions
---------

    % for f in functions:
<!-- python-${f.name.lower()}.md -->
${h1(f"`{f.name}`")}
${function(f)}

    % endfor
% endif

% if classes:
Classes
-------

    % for c in classes:
<!-- python-${c.name.lower()}.md -->
${h1(f"`{c.name}`")}
${class_(c)}

    % endfor
% endif
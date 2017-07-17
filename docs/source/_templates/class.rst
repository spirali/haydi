{{ name }}
{{ underline }}

.. currentmodule:: haydi

.. autoclass:: {{ objname }}

{% block methods %}
{% if methods %}
.. rubric:: Summary

.. autosummary::
{% for item in methods %}
   ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

.. rubric:: Methods

{% for item in methods %}
.. automethod:: {{name}}.{{item}}
{%- endfor %}


{{ name }}
{{ underline }}

.. currentmodule:: haydi

{% block methods %}
{% if methods %}
.. rubric:: Methods
.. autosummary::
{% for item in methods %}
   ~{{ name }}.{{ item }}
{%- endfor %}
{% endif %}
{% endblock %}

.. autoclass:: {{ objname }}
   :members:

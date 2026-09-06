"""Habilita la extensión btree_gist de PostgreSQL.

Es requisito de la ExclusionConstraint de `Reserva` (no-solapamiento de
reservas por espacio). Va en una migración propia y anterior a la de los
modelos para garantizar el orden: la siguiente migración de esta app
depende automáticamente de ésta.
"""

from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        BtreeGistExtension(),
    ]

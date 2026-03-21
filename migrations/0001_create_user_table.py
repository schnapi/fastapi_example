"""Auto-generated migration.

Created: 2026-03-19 21:29:13
"""

depends_on = None


def upgrade(ctx):
    """Apply migration."""
    ctx.create_table(
        "user",
        fields=[
            {
                'name': 'id',
                'python_type': 'int',
                'db_type': None,
                'nullable': True,
                'primary_key': True,
                'unique': False,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'username',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': False,
                'default': None,
                'auto_increment': False
            },
            {
                'name': 'email',
                'python_type': 'str',
                'db_type': None,
                'nullable': False,
                'primary_key': False,
                'unique': False,
                'default': None,
                'auto_increment': False
            }
        ],
    )


def downgrade(ctx):
    """Revert migration."""
    ctx.drop_table("user")

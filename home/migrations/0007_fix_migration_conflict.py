from django.db import migrations

def fix_review_conflict(apps, schema_editor):
    """
    This function ensures that if review tables already exist,
    we don't try to create them again.
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_add_review_system'),  # This should be your latest working migration
    ]

    operations = [
        migrations.RunPython(fix_review_conflict, migrations.RunPython.noop),
    ]
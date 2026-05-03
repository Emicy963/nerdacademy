from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("institutions", "0002_institution_institution_prefix"),
    ]

    operations = [
        migrations.AddField(
            model_name="institution",
            name="is_verified",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="institution",
            name="verification_token",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("bim_stock", "0016_receivingrecord_receivingitem"),
    ]

    operations = [
        migrations.AddField(
            model_name="receivingrecord",
            name="status",
            field=models.CharField(
                choices=[
                    ("recorded", "Recorded"),
                    ("cancelled", "Cancelled"),
                ],
                default="recorded",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="receivingrecord",
            name="cancel_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="receivingrecord",
            name="cancelled_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="receivingrecord",
            name="cancelled_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="cancelled_stock_receiving_records",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]

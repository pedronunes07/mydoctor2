from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todos', '0009_receita_destinatario'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='file_blob',
            field=models.BinaryField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recording',
            name='mime_type',
            field=models.CharField(default='video/webm', max_length=64),
        ),
        migrations.AlterField(
            model_name='recording',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='recordings/'),
        ),
    ]

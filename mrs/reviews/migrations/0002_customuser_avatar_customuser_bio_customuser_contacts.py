from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='Аватарка'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='bio',
            field=models.TextField(blank=True, null=True, verbose_name='Опис про себе'),
        ),
        migrations.AddField(
            model_name='customuser',
            name='contacts',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Контактна інформація'),
        ),
    ]

# Generated by Django 3.1.3 on 2021-12-18 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_client_border_size'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='border_size',
        ),
        migrations.RemoveField(
            model_name='client',
            name='encode_background_color',
        ),
        migrations.RemoveField(
            model_name='client',
            name='encode_shade',
        ),
        migrations.RemoveField(
            model_name='client',
            name='shade_direction',
        ),
        migrations.RemoveField(
            model_name='client',
            name='transparency',
        ),
        migrations.AddField(
            model_name='button',
            name='border_size',
            field=models.DecimalField(decimal_places=2, default=1.2, max_digits=10),
        ),
        migrations.AddField(
            model_name='button',
            name='encode_background_color',
            field=models.CharField(default='89_133_234', max_length=128),
        ),
        migrations.AddField(
            model_name='button',
            name='encode_shade',
            field=models.CharField(default='0_8_15_0.2', max_length=430),
        ),
        migrations.AddField(
            model_name='button',
            name='shade_direction',
            field=models.CharField(default='LEFT', max_length=128),
        ),
        migrations.AddField(
            model_name='button',
            name='transparency',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]

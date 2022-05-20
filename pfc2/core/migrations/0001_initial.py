# Generated by Django 3.1.3 on 2020-12-05 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('channel_ws', models.CharField(max_length=256)),
                ('token', models.CharField(max_length=8, unique=True)),
                ('center_x', models.IntegerField(default=0)),
                ('center_y', models.IntegerField(default=0)),
                ('options_x', models.IntegerField(default=0)),
                ('options_y', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Touch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('button', models.CharField(blank=True, choices=[('left', 'Left Button'), ('right', 'Right Button'), ('down', 'Down Button'), ('up', 'Up Button'), ('start', 'Start Button'), ('pause', 'Pause Button')], max_length=32, null=True)),
                ('position_x', models.IntegerField(default=0)),
                ('position_y', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='touches', to='core.client')),
            ],
        ),
    ]
# Generated by Django 2.2.10 on 2021-04-03 02:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('path_to_file', models.CharField(max_length=255, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='DetectedSmell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_smell_type', models.CharField(max_length=100)),
                ('total_element_count', models.IntegerField()),
                ('faulty_element_count', models.IntegerField()),
                ('mostly', models.FloatField()),
                ('belonging_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Column')),
                ('path_to_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.File')),
            ],
        ),
        migrations.AddField(
            model_name='column',
            name='belonging_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.File'),
        ),
    ]
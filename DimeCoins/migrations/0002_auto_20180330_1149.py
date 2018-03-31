# Generated by Django 2.0.1 on 2018-03-30 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DimeCoins', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(default='', max_length=50)),
                ('description', models.CharField(default='', max_length=255)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='currency',
            name='category',
            field=models.ManyToManyField(related_name='currencyCategory', to='DimeCoins.Category'),
        ),
    ]

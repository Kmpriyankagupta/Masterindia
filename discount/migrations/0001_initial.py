# Generated by Django 5.2 on 2025-04-16 16:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('discount_type', models.CharField(choices=[('cart', 'Overall Cart'), ('delivery', 'Delivery Charges')], max_length=10)),
                ('discount_value', models.DecimalField(decimal_places=2, help_text='Discount value (e.g. percentage or fixed amount)', max_digits=10)),
                ('start_date', models.DateTimeField(help_text='Campaign start date and time')),
                ('end_date', models.DateTimeField(help_text='Campaign end date and time')),
                ('total_budget', models.DecimalField(decimal_places=2, help_text='Max total discount budget available for this campaign', max_digits=10)),
                ('daily_usage_limit', models.IntegerField(default=1, help_text='Max transactions per customer per day')),
                ('used_budget', models.DecimalField(decimal_places=2, default=0, help_text='Budget used so far', max_digits=10)),
                ('allowed_customers', models.ManyToManyField(blank=True, help_text='If empty, campaign is available for all customers', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='DiscountUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('used_on', models.DateField(auto_now_add=True)),
                ('transaction_count', models.IntegerField(default=0)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages', to='discount.campaign')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount_usages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

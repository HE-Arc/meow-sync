# Generated migration for UserPlaylist model

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
			name='UserPlaylist',
			fields=[
				('id', models.BigAutoField(primary_key=True, serialize=False)),
				('created_at', models.DateTimeField(auto_now_add=True)),
				('updated_at', models.DateTimeField(auto_now=True)),
				('playlist_id', models.CharField(max_length=255)),
				(
					'provider',
					models.CharField(
						choices=[('spotify', 'Spotify'), ('youtube', 'Youtube')],
						max_length=255,
					),
				),
				('title', models.CharField(max_length=255)),
				('description', models.TextField(blank=True, null=True)),
				('author', models.CharField(max_length=255)),
				('img_url', models.CharField(blank=True, max_length=255, null=True)),
				(
					'user',
					models.ForeignKey(
						on_delete=django.db.models.deletion.CASCADE,
						to=settings.AUTH_USER_MODEL,
					),
				),
			],
			options={
				'abstract': False,
			},
		),
	]

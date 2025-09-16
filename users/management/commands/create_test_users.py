# Lütfen bu kodu kopyalayıp users/management/commands/create_test_users.py dosyasının içine yapıştırın.

import random
from faker import Faker
from datetime import time

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

# YENİ: Test verisi için koordinatları ile birlikte şehir listesi
TURKISH_CITIES = [
    {'name': 'İstanbul', 'lat': 41.0082, 'lon': 28.9784},
    {'name': 'Ankara', 'lat': 39.9334, 'lon': 32.8597},
    {'name': 'İzmir', 'lat': 38.4237, 'lon': 27.1428},
    {'name': 'Antalya', 'lat': 36.8969, 'lon': 30.7133},
    {'name': 'Bursa', 'lat': 40.1885, 'lon': 29.0610},
    {'name': 'Adana', 'lat': 37.0000, 'lon': 35.3213},
    {'name': 'Trabzon', 'lat': 41.0027, 'lon': 39.7168},
    {'name': 'Gaziantep', 'lat': 37.0662, 'lon': 37.3833},
    {'name': 'Diyarbakır', 'lat': 37.9140, 'lon': 40.2309},
    {'name': 'Eskişehir', 'lat': 39.7667, 'lon': 30.5256},
]

class Command(BaseCommand):
    help = 'Belirtilen sayıda rastgele test kullanıcısı oluşturur (koordinat bilgisiyle birlikte).'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Oluşturulacak kullanıcı sayısı')

    def handle(self, *args, **kwargs):
        count = kwargs['count']
        fake = Faker('tr_TR')
        created_count = 0

        self.stdout.write(self.style.NOTICE(f'{count} adet test kullanıcısı oluşturuluyor...'))

        for i in range(count):
            try:
                username = fake.user_name()
                email = f"{username}@example.com"
                password = "testpassword123"

                user = User.objects.create_user(username=username, email=email, password=password)
                profile = user.profile
                
                profile.gender = random.choice(['female', 'male'])
                profile.birth_date = fake.date_of_birth(minimum_age=18, maximum_age=45)
                profile.birth_time = time(random.randint(0, 23), random.randint(0, 59))
                
                # YENİ: Şehir, enlem ve boylamı rastgele listeden seç
                random_city = random.choice(TURKISH_CITIES)
                profile.birth_city = random_city['name']
                profile.latitude = random_city['lat']
                profile.longitude = random_city['lon']
                
                profile.bio = fake.paragraph(nb_sentences=3)
                
                # Bu kaydetme işlemi, güncelleyeceğimiz sinyali tetikleyecek.
                profile.save()
                
                created_count += 1
                self.stdout.write(f"'{username}' kullanıcısı ve profili ({profile.birth_city}) için oluşturuldu.")

            except IntegrityError:
                self.stdout.write(self.style.WARNING(f"Kullanıcı adı veya email zaten mevcut, atlanıyor."))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Bir kullanıcı oluşturulurken hata oluştu: {e}"))

        self.stdout.write(self.style.SUCCESS(f'İşlem tamamlandı. Toplam {created_count} yeni kullanıcı oluşturuldu.'))
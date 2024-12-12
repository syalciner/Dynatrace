******Scriptleri Çalıştırılabilir Hale Getirin
chmod +x disable_env.py
chmod +x enable_env.py

*********Cron Job Ayarlama
****Linux sistemde crontab dosyasını düzenleyin:
crontab -e

*************************Aşağıdaki satırları ekleyin:
# Her gün saat 22:00'de, Cumartesi ve Pazar hariç environment'ları DISABLED yap
0 22 * * 1-5 /usr/bin/python3 /path/to/disable_env.py

# Her gün saat 07:00'de, Cumartesi ve Pazar hariç environment'ları ENABLED yap
0 7 * * 1-5 /usr/bin/python3 /path/to/enable_env.py

********/usr/bin/python3: Python3'ün sisteminizdeki yolu. Farklı bir yol kullanıyorsanız bunu değiştirmelisiniz.
********/path/to/disable_env.py ve /path/to/enable_env.py: Python scriptlerinin bulunduğu tam yol.

********Cron Jobları Kontrol Etme
***Cron jobların başarıyla eklendiğinden emin olmak için:
crontab -l

****Loglama:
*****Cron job'ların çıktısını bir log dosyasına yönlendirebilirsiniz:

0 22 * * 1-5 /usr/bin/python3 /path/to/disable_env.py >> /path/to/disable_env.log 2>&1
0 7 * * 1-5 /usr/bin/python3 /path/to/enable_env.py >> /path/to/enable_env.log 2>&1

******Bu ayarlarla, disable_env.py scripti hafta içi her akşam saat 22:00'de çalışacak, enable_env.py scripti ise hafta içi her sabah saat 07:00'de çalışacaktır. Hafta sonları çalışmaz.

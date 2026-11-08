# Antigravity Kuralları

1. **Çoklu Dil (6 Dil Zorunlu):** Her yeni metin/arayüz elemanı istisnasız 6 dilde eklenecek: `tr`, `en`, `de`, `es`, `fr`, `it`. Tek dilli metin bırakma.
2. **Masaüstü Dosya Standardı:** `~/Masaüstü/` çıktıları yalnızca ana proje adı olacak: `RamordCast.apk`, `RamordCast.csv`. Sürüm/tarih eki ekleme.
3. **Sürüm Artışı:** Her derleme/güncellemede `versionName` yama sürümü, Google Play `versionCode` kesinlikle +1 artırılacak. `index.html` eşzamanlı güncellenecek.
4. **Çalışma Günlüğü:** Her mesajda yapılan işlem `~/Belgeler/günlük/<PROJE>/günlük.md` dosyasına tek bir Türkçe cümleyle eklenecek: `[YYYY-MM-DD HH:MM] Yapılan işlemin tek cümlelik özeti.`
5. **Deneyim Kaydı:** Mimari kararlar ve çözümler `~/Belgeler/deneyim/<PROJE>/deneyim.md` dosyasına eklenecek: `### [YYYY-MM-DD] Başlık` ve *"Şunu şöyle yaptık çünkü..."* formatında gerekçe belirtilecek.
6. **Deneyim İnceleme:** `deneyim.md` her mesajda okunmayacak; yalnızca yeni kütüphane ekleme, refactoring, geçmiş derleme/hata çözümü ve mimari kararlarda açılacak.
7. **Derleme Rolü:** Ajan yalnızca APK (`RamordCast.apk`) derleyecek; `.aab` paketlemesini kesinlikle kullanıcı yapacak.

# -*- coding: utf-8 -*-
"""
Ramord Cast Çoklu Dil Modülü (6 Dil Zorunlu: tr, en, de, es, fr, it)
"""

LANGUAGES = {
    "tr": "Türkçe",
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "fr": "Français",
    "it": "Italiano"
}

TRANSLATIONS = {
    # Başlık ve Genel
    "app_title": {
        "tr": "Ramord Cast",
        "en": "Ramord Cast",
        "de": "Ramord Cast",
        "es": "Ramord Cast",
        "fr": "Ramord Cast",
        "it": "Ramord Cast"
    },
    "app_subtitle": {
        "tr": "Samsung ve Tizen Ultra Düşük Gecikmeli Ekran Bağlantısı",
        "en": "Samsung and Tizen Ultra Low-Latency Screen Connection",
        "de": "Samsung und Tizen Ultra-Low-Latency Bildschirmverbindung",
        "es": "Conexión de Pantalla Samsung y Tizen de Ultra Baja Latencia",
        "fr": "Connexion d'Écran Samsung et Tizen à Ultra Faible Latence",
        "it": "Connessione Schermo Samsung e Tizen ad Ultra Bassa Latenza"
    },
    "status_ready": {
        "tr": "Hazır. Bağlantı yöntemini ve hedef monitörü seçin.",
        "en": "Ready. Select a connection method and target monitor.",
        "de": "Bereit. Wählen Sie eine Verbindungsmethode und einen Zielmonitor.",
        "es": "Listo. Seleccione un método de conexión y monitor de destino.",
        "fr": "Prêt. Sélectionnez une méthode de connexion et un moniteur cible.",
        "it": "Pronto. Seleziona un metodo di connessione e il monitor di destinazione."
    },
    "status_scanning": {
        "tr": "Ağdaki Samsung ve Tizen monitörler taranıyor...",
        "en": "Scanning network for Samsung and Tizen monitors...",
        "de": "Netzwerk nach Samsung- und Tizen-Monitoren durchsuchen...",
        "es": "Escaneando la red en busca de monitores Samsung y Tizen...",
        "fr": "Recherche de moniteurs Samsung et Tizen sur le réseau...",
        "it": "Scansione della rete per monitor Samsung e Tizen in corso..."
    },
    "status_connected": {
        "tr": "Bağlandı ve canlı çalışıyor!",
        "en": "Connected and streaming live!",
        "de": "Verbunden und live gestreamt!",
        "es": "¡Conectado y transmitiendo en vivo!",
        "fr": "Connecté et diffusé en direct !",
        "it": "Connesso e in trasmissione live!"
    },
    "status_connecting": {
        "tr": "Monitöre bağlanılıyor...",
        "en": "Connecting to monitor...",
        "de": "Verbindung zum Monitor wird hergestellt...",
        "es": "Conectando al monitor...",
        "fr": "Connexion au moniteur en cours...",
        "it": "Connessione al monitor in corso..."
    },

    # Butonlar
    "btn_start": {
        "tr": "Bağlantıyı Başlat",
        "en": "Start Connection",
        "de": "Verbindung starten",
        "es": "Iniciar Conexión",
        "fr": "Démarrer la Connexion",
        "it": "Avvia Connessione"
    },
    "btn_stop": {
        "tr": "Bağlantıyı Kes",
        "en": "Disconnect",
        "de": "Verbindung trennen",
        "es": "Desconectar",
        "fr": "Déconnecter",
        "it": "Disconnetti"
    },
    "btn_refresh": {
        "tr": "Cihazları Yeniden Tara",
        "en": "Rescan Devices",
        "de": "Geräte neu scannen",
        "es": "Volver a buscar dispositivos",
        "fr": "Analyser à nouveau les appareils",
        "it": "Scansiona di nuovo i dispositivi"
    },
    "btn_multiview": {
        "tr": "Multi View Böl / Değiştir",
        "en": "Toggle Multi View",
        "de": "Multi View umschalten",
        "es": "Alternar Multi View",
        "fr": "Basculer Multi View",
        "it": "Alterna Multi View"
    },

    # Bağlantı Teknolojisi and Protokol Seçimi
    "section_connection_type": {
        "tr": "Bağlantı Teknolojisi ve Protokol",
        "en": "Connection Technology and Protocol",
        "de": "Verbindungstechnologie und Protokoll",
        "es": "Tecnología de Conexión y Protocolo",
        "fr": "Technologie de Connexion et Protocole",
        "it": "Tecnologia di Connessione e Protocollo"
    },
    "proto_airplay": {
        "tr": "Apple AirPlay 2 (Önerilen - Donanımsal Hızlandırma, 60 FPS, Ultra Düşük Gecikme)",
        "en": "Apple AirPlay 2 (Recommended - Hardware Accel, 60 FPS, Ultra Low Latency)",
        "de": "Apple AirPlay 2 (Empfohlen - Hardware-Beschl., 60 FPS, Ultra-Niedrige Latenz)",
        "es": "Apple AirPlay 2 (Recomendado - Aceleración HW, 60 FPS, Ultra Baja Latencia)",
        "fr": "Apple AirPlay 2 (Recommandé - Accél. Matérielle, 60 FPS, Ultra Faible Latence)",
        "it": "Apple AirPlay 2 (Consigliato - Accel. HW, 60 FPS, Ultra Bassa Latenza)"
    },
    "proto_airplay_desc": {
        "tr": "Samsung M7 için donanım hızlandırmalı, sıfıra yakın gecikmeli canlı masaüstü akışı.",
        "en": "Hardware-accelerated, near-zero latency live desktop streaming for Samsung M7.",
        "de": "Hardware-beschleunigtes Live-Desktop-Streaming mit nahezu null Latenz für Samsung M7.",
        "es": "Transmisión de escritorio en vivo acelerada por hardware con latencia casi nula para Samsung M7.",
        "fr": "Diffusion de bureau en direct accélérée matériellement avec une latence quasi nulle pour Samsung M7.",
        "it": "Streaming desktop live accelerato via hardware con latenza quasi nulla per Samsung M7."
    },
    "proto_smartview": {
        "tr": "Samsung Smart View (Galaxy One UI 3.1+ Modu - Multi View Eşleştirme)",
        "en": "Samsung Smart View (Galaxy One UI 3.1+ Mode - Multi View Pairing)",
        "de": "Samsung Smart View (Galaxy One UI 3.1+ Modus - Multi View Kopplung)",
        "es": "Samsung Smart View (Modo Galaxy One UI 3.1+ - Emparejamiento Multi View)",
        "fr": "Samsung Smart View (Mode Galaxy One UI 3.1+ - Couplage Multi View)",
        "it": "Samsung Smart View (Modalità Galaxy One UI 3.1+ - Accoppiamento Multi View)"
    },
    "proto_smartview_desc": {
        "tr": "Bilgisayarı Samsung TV'ye Galaxy One UI 3.1+ Smart View cihazı olarak tanıtır; Multi View'da kaydetmeye uygundur.",
        "en": "Presents PC to Samsung TV as Galaxy One UI 3.1+ Smart View device; fully compatible with Multi View pairing.",
        "de": "Präsentiert PC als Galaxy One UI 3.1+ Smart View Gerät am Samsung TV; ideal für Multi View Kopplung.",
        "es": "Presenta la PC al televisor Samsung como dispositivo Galaxy One UI 3.1+ Smart View; apto para Multi View.",
        "fr": "Présente le PC au téléviseur Samsung comme appareil Galaxy One UI 3.1+ Smart View ; parfait pour Multi View.",
        "it": "Presenta il PC al televisore Samsung come dispositivo Galaxy One UI 3.1+ Smart View; adatto a Multi View."
    },
    "proto_bridge": {
        "tr": "Smart View Köprüsü (Multi View Uyumlu - Galaxy S23 ile Sıfır Gecikme)",
        "en": "Smart View Bridge (Multi View Compatible - Zero Latency via Galaxy S23)",
        "de": "Smart View Brücke (Multi View Kompatibel - Null Latenz über Galaxy S23)",
        "es": "Puente Smart View (Compatible con Multi View - Cero Latencia vía Galaxy S23)",
        "fr": "Passerelle Smart View (Compatible Multi View - Latence Zéro via Galaxy S23)",
        "it": "Ponte Smart View (Compatibile con Multi View - Latenza Zero via Galaxy S23)"
    },
    "proto_bridge_desc": {
        "tr": "Samsung Multi View bölünmüş ekran bölmesinde masaüstünü ultra düşük gecikmeyle yansıtın.",
        "en": "Mirror desktop with ultra-low latency directly inside Samsung Multi View split screen.",
        "de": "Desktop mit extrem niedriger Latenz direkt im geteilten Samsung Multi View-Bildschirm spiegeln.",
        "es": "Refleje el escritorio con latencia ultra baja directamente en la pantalla dividida Multi View de Samsung.",
        "fr": "Miroir du bureau à très faible latence directement dans l'écran partagé Samsung Multi View.",
        "it": "Duplica il desktop con latenza ultra bassa direttamente nello schermo diviso Samsung Multi View."
    },
    "proto_workspace": {
        "tr": "Samsung Workspace (PC on TV / RDP - Sanal Ekran, Klavye/Fare)",
        "en": "Samsung Workspace (PC on TV / RDP - Virtual Display, Keyboard/Mouse)",
        "de": "Samsung Workspace (PC on TV / RDP - Virtueller Bildschirm, Tastatur/Maus)",
        "es": "Samsung Workspace (PC on TV / RDP - Pantalla Virtual y Teclado/Ratón)",
        "fr": "Samsung Workspace (PC on TV / RDP - Écran Virtuel, Clavier/Souris)",
        "it": "Samsung Workspace (PC on TV / RDP - Schermo Virtuale e Tastiera/Mouse)"
    },
    "proto_miracast": {
        "tr": "Wi-Fi Direct / Miracast (Doğrudan Donanımsal Tünel)",
        "en": "Wi-Fi Direct / Miracast (Direct Hardware Tunnel)",
        "de": "Wi-Fi Direct / Miracast (Direkter Hardware-Tunnel)",
        "es": "Wi-Fi Direct / Miracast (Túnel de Hardware Directo)",
        "fr": "Wi-Fi Direct / Miracast (Tunnel Matériel Direct)",
        "it": "Wi-Fi Direct / Miracast (Tunnel Hardware Diretto)"
    },
    "proto_cast": {
        "tr": "Yedek: Google Cast (Multimedya ve Video Yayını)",
        "en": "Fallback: Google Cast (Multimedia and Video Casting)",
        "de": "Fallback: Google Cast (Multimedia und Video-Streaming)",
        "es": "Respaldo: Google Cast (Multimedia y Video)",
        "fr": "Secours: Google Cast (Multimédia et Vidéo)",
        "it": "Riserva: Google Cast (Multimedia e Video)"
    },

    # Performans, Renk ve Gecikme Ayarları
    "section_performance": {
        "tr": "Görüntü Kalitesi, Renk ve Tepki Hızı Ayarları",
        "en": "Image Quality, Color and Latency Settings",
        "de": "Bildqualität, Farb- und Latenzeinstellungen",
        "es": "Ajustes de Calidad de Imagen, Color y Latencia",
        "fr": "Paramètres de Qualité d'Image, Couleur et Latence",
        "it": "Impostazioni di Qualità Immagine, Colore e Latenza"
    },
    "fps_label": {
        "tr": "Kare Hızı (FPS)",
        "en": "Frame Rate (FPS)",
        "de": "Bildrate (FPS)",
        "es": "Tasa de Cuadros (FPS)",
        "fr": "Fréquence d'Images (FPS)",
        "it": "Frequenza dei Fotogrammi (FPS)"
    },
    "fps_30": {
        "tr": "30 FPS (Önerilen - Akıcı ve Takılmasız)",
        "en": "30 FPS (Recommended - Smooth and Stutter-Free)",
        "de": "30 FPS (Empfohlen - Flüssig und Ruckelfrei)",
        "es": "30 FPS (Recomendado - Fluido y Sin Tirones)",
        "fr": "30 FPS (Recommandé - Fluide et Sans Saccades)",
        "it": "30 FPS (Consigliato - Fluido e Senza Scatti)"
    },
    "fps_60": {
        "tr": "60 FPS (Yüksek Hız)",
        "en": "60 FPS (High Speed)",
        "de": "60 FPS (Hohe Geschwindigkeit)",
        "es": "60 FPS (Alta Velocidad)",
        "fr": "60 FPS (Haute Vitesse)",
        "it": "60 FPS (Alta Velocità)"
    },
    "quality_label": {
        "tr": "Renk ve Görüntü Kalitesi (Bitrate)",
        "en": "Color and Image Quality (Bitrate)",
        "de": "Farb- und Bildqualität (Bitrate)",
        "es": "Calidad de Color e Imagen (Bitrate)",
        "fr": "Qualité des Couleurs et de l'Image (Débit)",
        "it": "Qualità del Colore e dell'Immagine (Bitrate)"
    },
    "quality_auto": {
        "tr": "Otomatik (Önerilen - Dinamik Ağ ve Zengin Renk)",
        "en": "Automatic (Recommended - Dynamic Network and Rich Color)",
        "de": "Automatisch (Empfohlen - Dynamisches Netzwerk and Satte Farben)",
        "es": "Automático (Recomendado - Red Dinámica y Color Rico)",
        "fr": "Automatique (Recommandé - Réseau Dynamique et Couleurs Riches)",
        "it": "Automatico (Consigliato - Rete Dinamica e Colori Ricchi)"
    },
    "quality_high": {
        "tr": "Yüksek Kalite (20 Mbps)",
        "en": "High Quality (20 Mbps)",
        "de": "Hohe Qualität (20 Mbps)",
        "es": "Alta Calidad (20 Mbps)",
        "fr": "Haute Qualité (20 Mbps)",
        "it": "Alta Qualità (20 Mbps)"
    },
    "quality_standard": {
        "tr": "Standart (12 Mbps)",
        "en": "Standard (12 Mbps)",
        "de": "Standard (12 Mbps)",
        "es": "Estándar (12 Mbps)",
        "fr": "Standard (12 Mbps)",
        "it": "Standard (12 Mbps)"
    },
    "latency_target_label": {
        "tr": "Tepki Süresi Hedefi (Gecikme)",
        "en": "Playout Latency Target",
        "de": "Wiedergabelatenz-Ziel",
        "es": "Objetivo de Latencia de Respuesta",
        "fr": "Objectif de Latence de Restitution",
        "it": "Obiettivo di Latenza di Risposta"
    },
    "latency_auto": {
        "tr": "Otomatik (Önerilen - Sıfır Takılma ve Pürüzsüz Senkron)",
        "en": "Automatic (Recommended - Zero Stutter and Smooth Sync)",
        "de": "Automatisch (Empfohlen - Null Ruckeln and Glatte Synchronisation)",
        "es": "Automático (Recomendado - Cero Tirones y Sincronización Suave)",
        "fr": "Automatique (Recommandé - Zéro Saccade et Synchronisation Fluide)",
        "it": "Automatico (Consigliato - Zero Scatti e Sincronizzazione Fluida)"
    },
    "latency_20ms": {
        "tr": "20 ms (Ultra Düşük Gecikme)",
        "en": "20 ms (Ultra Low Latency)",
        "de": "20 ms (Ultra-Niedrige Latenz)",
        "es": "20 ms (Ultra Baja Latencia)",
        "fr": "20 ms (Ultra Faible Latence)",
        "it": "20 ms (Latenza Ultra Bassa)"
    },
    "latency_40ms": {
        "tr": "40 ms (Kararlı)",
        "en": "40 ms (Stable)",
        "de": "40 ms (Stabil)",
        "es": "40 ms (Estable)",
        "fr": "40 ms (Stable)",
        "it": "40 ms (Stabile)"
    },
    "codec_label": {
        "tr": "Video ve Renk Kodlayıcı",
        "en": "Video and Color Codec",
        "de": "Video- and Farbcodec",
        "es": "Códec de Video y Color",
        "fr": "Codec Vidéo et Couleur",
        "it": "Codec Video e Colore"
    },
    "codec_auto": {
        "tr": "Otomatik (En Uyumlu)",
        "en": "Auto (Best Compatibility)",
        "de": "Automatisch (Beste Kompatibilität)",
        "es": "Automático (Mejor Kompatibilität)",
        "fr": "Automatique (Meilleure Compatibilité)",
        "it": "Automatico (Migliore Compatibilità)"
    },
    "codec_h264": {
        "tr": "H.264 (Hızlı ve Donanım Hızlandırmalı)",
        "en": "H.264 (Fast and Hardware Accelerated)",
        "de": "H.264 (Schnell and Hardware-Beschleunigt)",
        "es": "H.264 (Rápido y Acelerado por HW)",
        "fr": "H.264 (Rapide et Accéléré Matériellement)",
        "it": "H.264 (Veloce e Accelerato via HW)"
    },
    "codec_hevc": {
        "tr": "HEVC / H.265 (Zengin Dinamik Renk)",
        "en": "HEVC / H.265 (Rich Dynamic Color)",
        "de": "HEVC / H.265 (Reiche Dynamische Farben)",
        "es": "HEVC / H.265 (Color Dinámico Rico)",
        "fr": "HEVC / H.265 (Couleur Dynamique Riche)",
        "it": "HEVC / H.265 (Colore Dinamico Ricco)"
    },

    # Samsung Workspace Kartı
    "workspace_info_title": {
        "tr": "Samsung M7 Workspace (PC on TV) Bağlantı Bilgileri",
        "en": "Samsung M7 Workspace (PC on TV) Connection Details",
        "de": "Samsung M7 Workspace (PC on TV) Verbindungsdetails",
        "es": "Detalles de Conexión Samsung M7 Workspace (PC on TV)",
        "fr": "Détails de Connexion Samsung M7 Workspace (PC on TV)",
        "it": "Dettagli di Connessione Samsung M7 Workspace (PC on TV)"
    },
    "workspace_guide": {
        "tr": "1. Monitörünüzde: Ana Sayfa -> Workspace -> PC -> Windows PC seçin.\n2. Aşağıdaki IP, Kullanıcı Adı ve Şifre ile anında bağlanın:",
        "en": "1. On monitor: Home -> Workspace -> PC -> Windows PC.\n2. Connect instantly using the IP, Username, and Password below:",
        "de": "1. Auf Monitor: Home -> Workspace -> PC -> Windows PC.\n2. Sofort mit der unten stehenden IP, Benutzer und Passwort verbinden:",
        "es": "1. En monitor: Inicio -> Workspace -> PC -> Windows PC.\n2. Conéctese al instante con la IP, Usuario y Contraseña abajo:",
        "fr": "1. Sur le moniteur : Accueil -> Workspace -> PC -> Windows PC.\n2. Connectez-vous avec l'IP, l'utilisateur et mot de passe ci-dessous :",
        "it": "1. Sul monitor: Home -> Workspace -> PC -> Windows PC.\n2. Connettiti subito con l'IP, l'utente e password qui sotto:"
    },
    "workspace_ip": {
        "tr": "Bilgisayar IP Adresi",
        "en": "Computer IP Address",
        "de": "Computer-IP-Adresse",
        "es": "Dirección IP del Equipo",
        "fr": "Adresse IP de l'Ordinateur",
        "it": "Indirizzo IP del Computer"
    },
    "workspace_user": {
        "tr": "Kullanıcı Adı",
        "en": "Username",
        "de": "Benutzername",
        "es": "Nombre de Usuario",
        "fr": "Nom d'Utilisateur",
        "it": "Nome Utente"
    },
    "workspace_password": {
        "tr": "Şifre",
        "en": "Password",
        "de": "Passwort",
        "es": "Contraseña",
        "fr": "Mot de passe",
        "it": "Password"
    },
    "workspace_port": {
        "tr": "RDP Portu",
        "en": "RDP Port",
        "de": "RDP-Port",
        "es": "Puerto RDP",
        "fr": "Port RDP",
        "it": "Porta RDP"
    },
    "workspace_btn_start": {
        "tr": "Workspace Servisini Başlat (Port 3389)",
        "en": "Start Workspace Service (Port 3389)",
        "de": "Workspace-Dienst starten (Port 3389)",
        "es": "Iniciar Servicio Workspace (Puerto 3389)",
        "fr": "Démarrer Service Workspace (Port 3389)",
        "it": "Avvia Servizio Workspace (Porta 3389)"
    },
    "workspace_btn_stop": {
        "tr": "Workspace Servisini Durdur",
        "en": "Stop Workspace Service",
        "de": "Workspace-Dienst stoppen",
        "es": "Detener Servicio Workspace",
        "fr": "Arrêter Service Workspace",
        "it": "Arresta Servizio Workspace"
    },
    "workspace_status_active": {
        "tr": "Workspace (RDP) servisi hazır ve dinliyor. Monitörden bağlanabilirsiniz.",
        "en": "Workspace (RDP) service is ready and listening. You can connect from monitor.",
        "de": "Workspace (RDP)-Dienst ist bereit. Sie können sich vom Monitor verbinden.",
        "es": "El servicio Workspace (RDP) está listo. Puede conectarse desde el monitor.",
        "fr": "Le service Workspace (RDP) est prêt. Vous pouvez vous connecter depuis le moniteur.",
        "it": "Il servizio Workspace (RDP) è pronto. Puoi connetterti dal monitor."
    },
    "workspace_status_inactive": {
        "tr": "Workspace servisi kapalı.",
        "en": "Workspace service stopped.",
        "de": "Workspace-Dienst gestoppt.",
        "es": "Servicio Workspace detenido.",
        "fr": "Service Workspace arrêté.",
        "it": "Servizio Workspace disattivato."
    },
    "btn_notify_tv": {
        "tr": "Monitörde Workspace'i Aç",
        "en": "Open Workspace on Monitor",
        "de": "Workspace auf Monitor öffnen",
        "es": "Abrir Workspace en el Monitor",
        "fr": "Ouvrir Workspace sur le Moniteur",
        "it": "Apri Workspace sul Monitor"
    },
    "notify_tv_success": {
        "tr": "Komut monitöre gönderildi!",
        "en": "Command sent to monitor!",
        "de": "Befehl an Monitor gesendet!",
        "es": "¡Comando enviado al monitor!",
        "fr": "Commande envoyée au moniteur !",
        "it": "Comando inviato al monitor!"
    },

    # Miracast Rehberi
    "miracast_guide": {
        "tr": "Wi-Fi Direct (P2P) tüneli doğrudan monitörün Wi-Fi çipine bağlanır. Monitörünüzde 'İzin Ver' onayını verin.",
        "en": "Wi-Fi Direct (P2P) tunnel connects directly to monitor's Wi-Fi chip. Accept 'Allow' on your monitor.",
        "de": "Wi-Fi Direct (P2P)-Tunnel verbindet sich direkt mit dem WLAN-Chip des Monitors. Bestätigen Sie 'Zulassen' auf dem Monitor.",
        "es": "El túnel Wi-Fi Direct (P2P) se conecta directo al chip Wi-Fi del monitor. Acepte 'Permitir' en el monitor.",
        "fr": "Le tunnel Wi-Fi Direct (P2P) se connecte directement à la puce Wi-Fi du moniteur. Acceptez 'Autoriser' sur le moniteur.",
        "it": "Il tunnel Wi-Fi Direct (P2P) si collega direttamente al chip Wi-Fi del monitor. Conferma 'Consenti' sul monitor."
    },

    # Ekran Modları
    "section_display_mode": {
        "tr": "Ekran Modu",
        "en": "Display Mode",
        "de": "Anzeigemodus",
        "es": "Modo de Pantalla",
        "fr": "Mode d'Affichage",
        "it": "Modalità Schermo"
    },
    "mode_clone": {
        "tr": "Ekranı Klonla (Ana Ekranı Aynala)",
        "en": "Clone Display (Mirror Main Screen)",
        "de": "Bildschirm klonen (Hauptbildschirm spiegeln)",
        "es": "Clonar Pantalla (Duplicar Pantalla Principal)",
        "fr": "Cloner l'Écran (Miroir de l'Écran Principal)",
        "it": "Duplica Schermo (Specchia Schermo Principale)"
    },
    "mode_extend": {
        "tr": "Ekranı Genişlet (Bağımsız İkinci Monitör)",
        "en": "Extend Display (Independent Second Monitor)",
        "de": "Bildschirm erweitern (Unabhängiger zweiter Monitor)",
        "es": "Extender Pantalla (Segundo Monitor Independiente)",
        "fr": "Étendre l'Écran (Deuxième Moniteur Indépendant)",
        "it": "Estendi Schermo (Secondo Monitor Indipendente)"
    },
    "mode_window": {
        "tr": "Tek Bir Pencereyi Yansıt",
        "en": "Cast a Single Window",
        "de": "Einzelnes Fenster streamen",
        "es": "Transmitir una Sola Ventana",
        "fr": "Diffuser une Seule Fenêtre",
        "it": "Trasmetti una Singola Finestra"
    },

    # Ekran Konumlandırma
    "section_position": {
        "tr": "İkinci Ekranın Fiziksel Konumu",
        "en": "Second Screen Physical Position",
        "de": "Physische Position des zweiten Bildschirms",
        "es": "Posición Física de la Segunda Pantalla",
        "fr": "Position Physique du Deuxième Écran",
        "it": "Posizione Fisica del Secondo Schermo"
    },
    "pos_right": {
        "tr": "Ana Ekranın Sağında (Varsayılan)",
        "en": "Right of Main Screen (Default)",
        "de": "Rechts vom Hauptbildschirm (Standard)",
        "es": "A la derecha de la pantalla principal (Predeterminado)",
        "fr": "À droite de l'écran principal (Par défaut)",
        "it": "A destra dello schermo principale (Predefinito)"
    },
    "pos_left": {
        "tr": "Ana Ekranın Solunda",
        "en": "Left of Main Screen",
        "de": "Links vom Hauptbildschirm",
        "es": "A la izquierda de la pantalla principal",
        "fr": "À gauche de l'écran principal",
        "it": "A sinistra dello schermo principale"
    },
    "pos_top": {
        "tr": "Ana Ekranın Üstünde",
        "en": "Above Main Screen",
        "de": "Über dem Hauptbildschirm",
        "es": "Encima de la pantalla principal",
        "fr": "Au-dessus de l'écran principal",
        "it": "Sopra lo schermo principale"
    },
    "pos_bottom": {
        "tr": "Ana Ekranın Altında",
        "en": "Below Main Screen",
        "de": "Unter dem Hauptbildschirm",
        "es": "Debajo de la pantalla principal",
        "fr": "En dessous de l'écran principal",
        "it": "Sotto lo schermo principale"
    },

    # Hedef Cihazlar
    "section_targets": {
        "tr": "Bulunan Cihazlar",
        "en": "Discovered Devices",
        "de": "Gefundene Geräte",
        "es": "Dispositivos Encontrados",
        "fr": "Appareils Détectés",
        "it": "Dispositivi Rilevati"
    },
    "no_devices": {
        "tr": "Henüz bir cihaz bulunamadı. Lütfen monitörün açık ve aynı Wi-Fi ağında olduğundan emin olun.",
        "en": "No devices found yet. Please make sure monitor is on and on the same Wi-Fi network.",
        "de": "Noch keine Geräte gefunden. Bitte stellen Sie sicher, dass der Monitor eingeschaltet und im selben WLAN ist.",
        "es": "No se encontraron dispositivos aún. Asegúrese de que el monitor esté encendido y en la misma red Wi-Fi.",
        "fr": "Aucun appareil trouvé pour le moment. Veuillez vérifier que le moniteur est allumé et sur le même réseau Wi-Fi.",
        "it": "Nessun dispositivo ancora trovato. Assicurati che il monitor sia acceso e sulla stessa rete Wi-Fi."
    },
    "language_label": {
        "tr": "Dil",
        "en": "Language",
        "de": "Sprache",
        "es": "Idioma",
        "fr": "Langue",
        "it": "Lingua"
    }
}

def t(key, lang="tr"):
    """Metin anahtarını istenen dilde getirir."""
    if key in TRANSLATIONS:
        return TRANSLATIONS[key].get(lang, TRANSLATIONS[key].get("tr", key))
    return key

<img width="2816" height="1536" alt="Group 1 (5)" src="https://github.com/user-attachments/assets/6ce2727b-1dc7-4974-935a-61ec834080e5" />


# Mini SOC Architecture: Advanced Wazuh SIEM & Shuffle SOAR Integration

[![Wazuh](https://img.shields.io/badge/SIEM-Wazuh-blue?logo=wazuh)](https://wazuh.com/)
[![Shuffle](https://img.shields.io/badge/SOAR-Shuffle-purple?logo=shuffle)](https://shuffler.io/)
[![Python](https://img.shields.io/badge/Middleware-Python_3-yellow?logo=python)](https://www.python.org/)
[![Discord](https://img.shields.io/badge/Alerting-Discord-5865F2?logo=discord)](https://discord.com/)
[![Azure](https://img.shields.io/badge/Infrastructure-Microsoft_Azure-0089D6?logo=microsoft-azure)](https://azure.microsoft.com/)

Proyek ini adalah implementasi **Security Operations Center (SOC)** terintegrasi skala menengah. Sistem ini menggabungkan kemampuan deteksi ancaman tingkat lanjut (SIEM) menggunakan **Wazuh**, mitigasi serangan otomatis (*Active Response*), serta orkestrasi dan otomatisasi respons keamanan (SOAR) memanfaatkan **Shuffle** yang dihubungkan langsung ke *channel* peringatan **Discord**.

---

## Anggota Kelompok
* **Zein Muhammad Hasan** (5027241035)
* **Christiano Ronaldo Silalahi** (5027241025)
* **Jofanka Al-kaushar Pangestu Abady** (5027241107)
* **Oscaryavat Viryavan** (5027241053)

---

## Latar Belakang & Tujuan
Dengan meningkatnya intensitas serangan siber otomatis terhadap aplikasi web, pemantauan log secara manual tidak lagi efisien. Proyek ini bertujuan untuk membangun infrastruktur pertahanan yang mampu:
1. **Mendeteksi** anomali dan vektor serangan web secara *real-time*.
2. **Memitigasi** serangan secara instan tanpa campur tangan administrator.
3. **Melaporkan** insiden dengan metrik yang kaya dan mudah dibaca (JSON ke Rich-Text) melalui *platform* komunikasi tim.

---

## Fitur Utama & Kemampuan Sistem

### 1. Advanced SIEM & Custom Threat Detection (Wazuh)
Sistem ini tidak hanya mengandalkan aturan bawaan, tetapi juga diperkuat dengan *Custom XML Rules* yang dirancang khusus untuk membedah log Nginx. Sistem mampu mendeteksi vektor serangan berikut:
* **DDoS & DoS Attacks:** Memantau ambang batas *traffic* (contoh: >50 *requests* dalam 10 detik dari IP yang sama) menggunakan rule *frequency* dan *timeframe*.
* **Web Vulnerability Exploitation:** Mendeteksi upaya *SQL Injection (SQLi)*, *Cross-Site Scripting (XSS)*, dan *Directory Traversal*.
* **Malicious File Uploads:** Mendeteksi upaya injeksi *Web Shell* (misal: `shell.php`, `.php.jpg`).
* **Reconnaissance & Scanning:** Mengenali jejak dari pemindai kerentanan otomatis seperti *Nmap Scripting Engine (NSE)* dan *User-Agent* mencurigakan.

### 2. Auto-Mitigation / Active Response (Firewall Drop)
Sebagai langkah pertahanan preventif, Wazuh dikonfigurasi sebagai *Intrusion Prevention System (IPS)*:
* Menggunakan modul eksekutor `firewall-drop` bawaan Wazuh.
* Sistem secara otomatis menyisipkan aturan blokir (*Drop*) ke dalam **iptables** Linux milik agen target seketika setelah *alert* Level 10 atau *brute-force* tercapai.
* Dilengkapi mekanisme *Timeout* selama 300 detik (5 Menit) untuk mencegah pemblokiran IP permanen yang tidak disengaja (*False Positive*).

### 3. Python-Based SOAR Middleware (Custom Integration)
Untuk menghubungkan Wazuh (yang berjalan di mesin terisolasi) dengan ekosistem internet (*Cloud SOAR*), sistem menggunakan *middleware* Python kustom:
* **JSON Payload Parsing:** Menangkap log deteksi Wazuh (`sys.argv[1]`) dan mengekstrak *metadata* penting (IP *Attacker*, Target Agent, Detail Rule).
* **SSL Verification Bypass:** Mengimplementasikan modul `ssl.CERT_NONE` dan manipulasi *context* HTTP untuk menembus isolasi mesin Python Wazuh saat melakukan POST *request* ke API eksternal berbasis HTTPS.
* **Fail-Safe Logging:** Menggunakan sistem *debugger log* lokal (`shuffle_debug.log`) untuk mencatat kode HTTP `200 OK` atau kegagalan transmisi tanpa mengganggu operasional Wazuh Manager.

### 4. Visual Orchestration & Real-Time Alerting (Shuffle + Discord)
Integrasi *pipeline* peringatan insiden tanpa *coding* (*No-Code*) menggunakan arsitektur visual:
* **Webhook Receiver:** Shuffle Cloud menerima transmisi JSON mentah dari Wazuh secara instan.
* **Data Transformation:** Mengubah variabel dinamis (seperti `$exec.agent.name` dan `$exec.data.srcip`) ke dalam format *Rich-Text*.
* **Discord Integration:** Mendorong pesan peringatan darurat ke dalam *channel* `#soc-alerts` di Discord sehingga tim analis dapat merespons insiden di mana saja dan kapan saja.

---

## Arsitektur Topologi Jaringan

*(Sematkan Gambar Diagram Alur SOC Di Sini)*

Infrastruktur ini di-*deploy* di atas lingkungan Microsoft Azure Virtual Machines:

| Node | Peran / Layanan | Deskripsi Fungsi |
| :--- | :--- | :--- |
| **VM 1** | **Wazuh Manager** | Pusat analitik (SIEM), penyimpan *Custom Rules*, pusat kendali *Active Response*, dan *host* untuk *Python Middleware*. |
| **VM 2** | **Target-Web** | *Web Server* Nginx yang diinstal *Wazuh Agent* untuk memantau log akses HTTP secara *real-time*. |
| **VM 3** | **Target-DB** | Server *Database* dengan *Wazuh Agent* untuk memantau upaya *Brute-Force Auth* (SSH/Login). |
| **Cloud** | **Shuffle SOAR** | *Workflow Automation* (Penerima *Webhook*, Pengolah JSON). |
| **Cloud** | **Discord** | *Endpoint* akhir untuk notifikasi tim. |

---

## Alur Kerja Sistem (Attack-to-Alert Lifecycle)

Sistem bekerja secara linear dan otomatis dalam hitungan milidetik (*Milliseconds*):
1. **[Attack Phase]** Penyerang (`Attacker IP: 182.8.99.x`) membanjiri Target-Web dengan *traffic* buatan (DDoS).
<img width="552" height="586" alt="Screenshot 2026-06-01 201959" src="https://github.com/user-attachments/assets/215d9605-441c-4c62-98cf-468309bec9a0" />

2. **[Ingestion Phase]** Nginx mencatat aktivitas tersebut ke dalam `access.log`. *Wazuh Agent* secara *real-time* meneruskan log ini ke Manager.
<img width="1561" height="443" alt="Screenshot 2026-06-01 202718" src="https://github.com/user-attachments/assets/b20aabc6-3e4b-421c-b579-f42185545d0e" />

3. **[Correlation Phase]** Otak Wazuh Manager membandingkan log tersebut dengan *Custom Rules*. Rule `100113` terpicu akibat pelanggaran *threshold* frekuensi serangan.
4. **[Action Phase - Forking]** Manager memicu dua tindakan serentak:
   * **Mitigasi:** Mengirim *command* `firewall-drop` kembali ke Agent, yang langsung memutus akses IP penyerang di *Firewall* lokal.
   <img width="589" height="117" alt="Screenshot 2026-06-01 202748" src="https://github.com/user-attachments/assets/511e7d62-85a6-47c9-8ff8-157f486160c3" />
   
   * **Integrasi:** Memanggil *script* `custom-shuffle` untuk mengirimkan ringkasan insiden ke URL Webhook Shuffle.
   <img width="488" height="868" alt="Screenshot 2026-06-01 202523" src="https://github.com/user-attachments/assets/97608599-e303-4f7a-9fe1-decd61d15275" />
   
5. **[Orchestration Phase]** Shuffle memproses *payload* JSON, merakit struktur pesan peringatan, dan membunyikan alarm di *channel* Discord tim SOC.
<img width="1397" height="230" alt="Screenshot 2026-06-01 202139" src="https://github.com/user-attachments/assets/8a7542da-102c-442f-af6a-9e574e25a42b" />
---

## Tech Stack & Requirements
* **OS:** Ubuntu 22.04 / 24.04 LTS (Azure VM)
* **SIEM:** Wazuh v4.x (Manager & Agent)
* **Web Server:** Nginx
* **Language:** Python 3 (Framework Wazuh) + Bash Scripting
* **External Services:** Shuffler.io, Discord Webhooks

---

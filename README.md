# FuCH3CKeR

**FuCH3CKeR** adalah alat *all-in-one* yang memudahkan kamu untuk mengecek kredensial dari berbagai platform seperti **SendGrid**, **Twilio**, **AWS SES**, dan **IAM**. Nggak cuma cek API key, FuCH3CKeR juga bisa ngecek kuota, ngirim email, bahkan bikin kredensial SMTP AWS SES secara otomatis plus tes kirim email! Alat ini cocok banget buat developer atau admin yang pengen hidup lebih mudah.

## ✨ Fitur

- **Cek Balance Sendgrid**
- **Cek Balance Twilio**
- **Cek Balance Nexmo** new!
- **Cek Stripe Api Key** new!
- **Cek Balance Amazon SES**
- **Cek IAM Permission**
- **Buat Kredensial SMTP AWS SES**
- 📂 **Dukungan Bulk Check**: Cek kredensial secara massal dari file.
## Persyaratan

- **Python 3.7+**
- Install paket Python yang diperlukan:

  ```bash
  pip install boto3 requests twilio pyfiglet colorama
  ```
  
  ## Penggunaan

1. **Clone Repositori:**

   Clone repositori ini ke direktori lokal Anda:

   ```bash
   git clone https://github.com/adtyaff/FuCH3CKeR.git
   cd FuCH3CKeR
   ```
 
2. **Run Program**

   Run script nya dengan perintah
   
  ```bash
   python fuch3cker.py
   ```

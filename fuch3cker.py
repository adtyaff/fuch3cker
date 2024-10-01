import os
import requests
import boto3
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from botocore.exceptions import ClientError
from colorama import Fore, Style
import pyfiglet
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def tampil_logo():
    logo = pyfiglet.figlet_format("FuCH3CKeR", font="slant")
    header = (
        f"{Fore.YELLOW}{logo}{Style.RESET_ALL}\n"
        f"{Style.BRIGHT}Author: AdtyaF{Style.RESET_ALL} | "
        f"{Style.BRIGHT}Last Update: 2024-10-01{Style.RESET_ALL}\n"
    )
    print(header)


def reset_clear():
    if os.name == "posix":
        _ = os.system("clear")
    else:
        _ = os.system("cls")


def cek_sendgrid_kuota(apikey, verbose=True):
    if verbose:
        print(f"{Fore.CYAN}[INFO] Checking.... {Style.RESET_ALL}")

    url = "https://api.sendgrid.com/v3/user/credits"
    headers = {"Authorization": f"Bearer {apikey}", "Content-Type": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        total_kuota = data.get("total", "Tidak tersedia")
        sisa_kuota = data.get("remaining", "Tidak tersedia")
        reset_frek = data.get("reset_frequency", "Tidak tersedia")

        result = (
            f"{Style.BRIGHT}ApiKey: {Style.RESET_ALL}{apikey}\n"
            f"{Style.BRIGHT}Limit: {Style.RESET_ALL}{total_kuota}\n"
            f"{Style.BRIGHT}Used: {Style.RESET_ALL}{int(total_kuota) - int(sisa_kuota)}\n"
            f"{Style.BRIGHT}Reset Frequency: {Style.RESET_ALL}{reset_frek}\n"
        )
        result += "-" * 40

        if verbose:
            print(f"{Fore.GREEN}[SIP] API Key SendGrid beres dicek!{Style.RESET_ALL}")
        return True, result

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        error_message = (
            f"{Style.BRIGHT}Waduh! Gagal cek API Key SendGrid!\n"
            f"{Style.BRIGHT}ApiKey: {Style.RESET_ALL}{apikey}\n"
            f"{Style.BRIGHT}Status Code: {Style.RESET_ALL}{status_code}\n"
            f"{Style.BRIGHT}Pesan Error: {Style.RESET_ALL}{e.response.text}\n"
        )
        error_message += "-" * 40

        if verbose:
            print(
                f"{Fore.RED}[ERROR] Ada masalah! Status Code {status_code}{Style.RESET_ALL}"
            )
        return False, error_message


def cek_twilio_info(account_sid, auth_token, verbose=True):
    if verbose:
        print(f"{Fore.CYAN}[INFO] Checking.... {Style.RESET_ALL}")

    try:
        client = Client(account_sid, auth_token)
        balance_url = (
            f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Balance.json"
        )
        balance_response = requests.get(balance_url, auth=(account_sid, auth_token))

        if balance_response.status_code == 200:
            balance_data = balance_response.json()
            saldo = balance_data["balance"]
            mata_uang = balance_data["currency"]
        else:
            saldo = "Tidak ketahuan"
            mata_uang = "Tidak ketahuan"

        account_info = client.api.accounts(account_sid).fetch()
        tipe_akun = "Trial" if account_info.status == "trial" else "Full"

        incoming_numbers = client.incoming_phone_numbers.list()
        nomor_list = [number.phone_number for number in incoming_numbers]

        result = (
            f"{Style.BRIGHT}Account SID: {Style.RESET_ALL}{account_sid}\n"
            f"{Style.BRIGHT}Auth Token: {Style.RESET_ALL}{auth_token}\n"
            f"{Style.BRIGHT}Tipe Akun: {Style.RESET_ALL}{tipe_akun}\n"
            f"{Style.BRIGHT}Balance: {Style.RESET_ALL}{saldo} {mata_uang}\n"
            f"{Style.BRIGHT}Available Numbers:{Style.RESET_ALL}\n"
        )
        result += "\n".join([f" - {nomor}" for nomor in nomor_list]) + "\n"
        result += "-" * 40

        if verbose:
            print(f"{Fore.GREEN}[SIP] Twilio udah beres dicek!{Style.RESET_ALL}")
        return True, result

    except TwilioRestException as e:
        error_message = (
            f"{Style.BRIGHT}Waduh! Gagal Ambil Data Twilio!\n"
            f"{Style.BRIGHT}Account SID: {Style.RESET_ALL}{account_sid}\n"
            f"{Style.BRIGHT}Auth Token: {Style.RESET_ALL}{auth_token}\n"
            f"{Style.BRIGHT}Error Code: {Style.RESET_ALL}{getattr(e, 'code', 'N/A')}\n"
            f"{Style.BRIGHT}Status Code: {Style.RESET_ALL}{e.status}\n"
            f"{Style.BRIGHT}Pesan Error: {Style.RESET_ALL}{e.msg}\n"
        )
        error_message += "-" * 40

        if verbose:
            print(f"{Fore.RED}[ERROR] Masalah! Status Code {e.status}{Style.RESET_ALL}")
        return False, error_message


def cek_aws_ses_limit(aws_access_key, aws_secret_key, region, verbose=True):
    if verbose:
        print(f"{Fore.CYAN}[INFO] Checking.... {Style.RESET_ALL}")

    try:
        client = boto3.client(
            "ses",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region,
        )

        send_quota = client.get_send_quota()
        enforcement_status = client.get_account_sending_enabled()

        result = (
            f"{Style.BRIGHT}AWS Access Key: {Style.RESET_ALL}{aws_access_key}\n"
            f"{Style.BRIGHT}AWS Secret Key: {Style.RESET_ALL}{aws_secret_key}\n"
            f"{Style.BRIGHT}Region: {Style.RESET_ALL}{region}\n"
            f"{Style.BRIGHT}Enforcement Status: {Style.RESET_ALL}{'Enabled' if enforcement_status['Enabled'] else 'Disabled'}\n"
            f"{Style.BRIGHT}Max24HourSend: {Style.RESET_ALL}{send_quota['Max24HourSend']}\n"
            f"{Style.BRIGHT}MaxSendRate: {Style.RESET_ALL}{send_quota['MaxSendRate']}\n"
            f"{Style.BRIGHT}SentLast24Hours: {Style.RESET_ALL}{send_quota['SentLast24Hours']}\n"
        )
        result += "-" * 40

        if verbose:
            print(f"{Fore.GREEN}[SIP] AWS SES sukses dicek!{Style.RESET_ALL}")
        return True, result

    except ClientError as e:
        error_message = (
            f"{Style.BRIGHT}Waduh! Gagal Ambil Data AWS SES!\n"
            f"{Style.BRIGHT}AWS Access Key: {Style.RESET_ALL}{aws_access_key}\n"
            f"{Style.BRIGHT}AWS Secret Key: {Style.RESET_ALL}{aws_secret_key}\n"
            f"{Style.BRIGHT}Region: {Style.RESET_ALL}{region}\n"
            f"{Style.BRIGHT}Error Code: {Style.RESET_ALL}{e.response['Error']['Code']}\n"
            f"{Style.BRIGHT}Pesan Error: {Style.RESET_ALL}{e.response['Error']['Message']}\n"
        )
        error_message += "-" * 40

        if verbose:
            print(
                f"{Fore.RED}[ERROR] Gagal, Error: {e.response['Error']['Code']}{Style.RESET_ALL}"
            )
        return False, error_message


def create_smtp_and_test_email(
    aws_access_key, aws_secret_key, region, test_email, verbose=True
):
    if verbose:
        print(f"{Fore.CYAN}[INFO] Creating.... {Style.RESET_ALL}")

    try:
        client = boto3.client(
            "ses",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region,
        )

        response = client.create_smtp_credentials()
        smtp_username = response["SmtpUsername"]
        smtp_password = response["SmtpPassword"]

        email_from = client.get_identity_mail_from_domain_attributes()

        message = MIMEMultipart()
        message["From"] = email_from
        message["To"] = test_email
        message["Subject"] = "FuCH3KeR - adtyaF"

        body = "Test Email"
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("email-smtp." + region + ".amazonaws.com", 587) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(email_from, test_email, message.as_string())

        result = (
            f"{Style.BRIGHT}SMTP Username: {Style.RESET_ALL}{smtp_username}\n"
            f"{Style.BRIGHT}SMTP Password: {Style.RESET_ALL}{smtp_password}\n"
            f"{Style.BRIGHT}From Email: {Style.RESET_ALL}{email_from}\n"
            f"{Style.BRIGHT}Port: {Style.RESET_ALL}587\n"
        )

        if verbose:
            print(f"{Fore.GREEN}[SIP] Sukses Test Send!{Style.RESET_ALL}")
        return True, result

    except ClientError as e:
        error_message = (
            f"{Style.BRIGHT}Waduh! Gagal Buat SMTP AWS SES!\n"
            f"{Style.BRIGHT}AWS Access Key: {Style.RESET_ALL}{aws_access_key}\n"
            f"{Style.BRIGHT}AWS Secret Key: {Style.RESET_ALL}{aws_secret_key}\n"
            f"{Style.BRIGHT}Region: {Style.RESET_ALL}{region}\n"
            f"{Style.BRIGHT}Error Code: {Style.RESET_ALL}{e.response['Error']['Code']}\n"
            f"{Style.BRIGHT}Pesan Error: {Style.RESET_ALL}{e.response['Error']['Message']}\n"
        )
        error_message += "-" * 40

        if verbose:
            print(
                f"{Fore.RED}[ERROR] Gagal buat SMTP: {e.response['Error']['Code']}{Style.RESET_ALL}"
            )
        return False, error_message


def main():
    reset_clear()
    tampil_logo()
    print(Fore.YELLOW + Style.BRIGHT + "Mau cek apa?" + Style.RESET_ALL)
    print(f"Ketik '{Fore.YELLOW}{Style.BRIGHT}sg{Style.RESET_ALL}' untuk cek SendGrid")
    print(f"Ketik '{Fore.YELLOW}{Style.BRIGHT}tw{Style.RESET_ALL}' untuk cek Twilio")
    print(
        f"Ketik '{Fore.YELLOW}{Style.BRIGHT}ses{Style.RESET_ALL}' untuk cek Amazon SES"
    )
    print(
        f"Ketik '{Fore.YELLOW}{Style.BRIGHT}iam{Style.RESET_ALL}' untuk cek IAM Permissions"
    )
    print(
        f"Ketik '{Fore.YELLOW}{Style.BRIGHT}cses{Style.RESET_ALL}' untuk buat kredensial SMTP SES + Test Send Email"
    )
    print(f"Ketik '{Fore.RED}{Style.BRIGHT}keluar{Style.RESET_ALL}' kalo mau cabut")

    pilihan = input(
        Fore.YELLOW + Style.BRIGHT + "\nPilih Checker: " + Style.RESET_ALL
    ).lower()

    if pilihan == "sg":
        reset_clear()
        tampil_logo()
        opsi = input(
            Style.BRIGHT
            + "Mau cek 'ecer' satu-satu, atau 'bulk' langsung dari list?: "
            + Style.RESET_ALL
        ).lower()
        if opsi == "ecer":
            apikey = input(Style.BRIGHT + "SendGrid API Key: " + Style.RESET_ALL)
            status, result = cek_sendgrid_kuota(apikey)
            simpan_output("res_sendgrid", status, result)
        elif opsi == "bulk":
            filename = input(
                Style.BRIGHT + "list? (contoh: list_sendgrid.txt): " + Style.RESET_ALL
            )
            cek_bulk_sendgrid(filename)

    elif pilihan == "tw":
        reset_clear()
        tampil_logo()
        opsi = input(
            Style.BRIGHT
            + "Mau cek 'ecer' satu-satu, atau 'bulk' langsung dari list?: "
            + Style.RESET_ALL
        ).lower()
        if opsi == "ecer":
            account_sid = input(Style.BRIGHT + "Twilio Account SID: " + Style.RESET_ALL)
            auth_token = input(Style.BRIGHT + "Twilio Auth Token: " + Style.RESET_ALL)
            status, result = cek_twilio_info(account_sid, auth_token)
            simpan_output("res_twilio", status, result)
        elif opsi == "bulk":
            filename = input(
                Style.BRIGHT + "list? (contoh: list_twilio.txt): " + Style.RESET_ALL
            )
            cek_bulk_twilio(filename)

    elif pilihan == "ses":
        reset_clear()
        tampil_logo()
        opsi = input(
            Style.BRIGHT
            + "Mau cek 'ecer' satu-satu, atau 'bulk' langsung dari list?: "
            + Style.RESET_ALL
        ).lower()
        if opsi == "ecer":
            aws_key = input(Style.BRIGHT + "AWS Access Key: " + Style.RESET_ALL)
            aws_secret = input(Style.BRIGHT + "AWS Secret Key: " + Style.RESET_ALL)
            aws_region = input(
                Style.BRIGHT + "AWS Region (contoh: us-east-1): " + Style.RESET_ALL
            )
            status, result = cek_aws_ses_limit(aws_key, aws_secret, aws_region)
            simpan_output("res_amzses", status, result)
        elif opsi == "bulk":
            filename = input(
                Style.BRIGHT + "list? (contoh: list_ses.txt): " + Style.RESET_ALL
            )
            cek_bulk_ses(filename)

    elif pilihan == "iam":
        reset_clear()
        tampil_logo()
        aws_key = input(Style.BRIGHT + "AWS Access Key: " + Style.RESET_ALL)
        aws_secret = input(Style.BRIGHT + "AWS Secret Key: " + Style.RESET_ALL)
        aws_region = input(
            Style.BRIGHT + "AWS Region (contoh: us-east-1): " + Style.RESET_ALL
        )
        status, result = cek_aws_iam_permission(aws_key, aws_secret, aws_region)
        simpan_output("res_iam", status, result)

    elif pilihan == "cses":
        reset_clear()
        tampil_logo()
        aws_key = input(Style.BRIGHT + "AWS Access Key: " + Style.RESET_ALL)
        aws_secret = input(Style.BRIGHT + "AWS Secret Key: " + Style.RESET_ALL)
        aws_region = input(
            Style.BRIGHT + "AWS Region (contoh: us-east-1): " + Style.RESET_ALL
        )
        test_email = input(
            Style.BRIGHT + "Email tujuan untuk tes kirim: " + Style.RESET_ALL
        )
        status, result = create_smtp_and_test_email(
            aws_key, aws_secret, aws_region, test_email
        )
        simpan_output("res_smtp", status, result)

    elif pilihan == "keluar":
        print(Fore.RED + Style.BRIGHT + "Oke, Keluar!" + Style.RESET_ALL)
        return
    else:
        print(Fore.RED + Style.BRIGHT + "Pilihan gak valid!" + Style.RESET_ALL)
        main()


def simpan_output(folder, status, result):
    if not os.path.exists(folder):
        os.makedirs(folder)

    file = "mantap.txt" if status else "ampas.txt"
    with open(os.path.join(folder, file), "a") as f:
        f.write(result + "\n")


def cek_bulk_sendgrid(filename):
    try:
        with open(filename, "r") as f:
            for line in f:
                apikey = line.strip()
                status, result = cek_sendgrid_kuota(apikey)
                simpan_output("res_sendgrid", status, result)
    except FileNotFoundError:
        print(
            Fore.RED
            + f"File {filename} gaada. Periksa lagi nama file nya!"
            + Fore.RESET
        )
        cek_bulk_sendgrid(
            input(
                Style.BRIGHT + "list? (contoh: list_sendgrid.txt): " + Style.RESET_ALL
            )
        )


def cek_bulk_twilio(filename):
    try:
        with open(filename, "r") as f:
            for line in f:
                account_sid, auth_token = line.strip().split(":")
                status, result = cek_twilio_info(account_sid, auth_token)
                simpan_output("res_twilio", status, result)
    except FileNotFoundError:
        print(
            Fore.RED
            + f"File {filename} gaada. Periksa lagi nama file nya!"
            + Fore.RESET
        )
        cek_bulk_twilio(
            input(Style.BRIGHT + "list? (contoh: list_twilio.txt): " + Style.RESET_ALL)
        )


def cek_bulk_ses(filename):
    try:
        with open(filename, "r") as f:
            for line in f:
                aws_key, aws_secret, aws_region = line.strip().split(":")
                status, result = cek_aws_ses_limit(aws_key, aws_secret, aws_region)
                simpan_output("res_amzses", status, result)
    except FileNotFoundError:
        print(
            Fore.RED
            + f"File {filename} gaada. Periksa lagi nama file nya!"
            + Fore.RESET
        )
        cek_bulk_ses(
            input(Style.BRIGHT + "list? (contoh: list_ses.txt): " + Style.RESET_ALL)
        )


if __name__ == "__main__":
    main()
        

import random
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# --- PENGATURAN ---
EMAIL_LO = "Ganti dengan email/username"
PASSWORD_LO = "Ganti dengan password"
URL_POSTINGAN = "Ganti dengan URL postingan target"
KOMENTAR_LO = [
    "ramaikan",
    "akun murah",
    "gasskan bang",
    "dijamin aman",
]
JEDA_WAKTU = 5
JEDA_ANTAR_KOMENTAR_MIN = 15
JEDA_ANTAR_KOMENTAR_MAX = 25
MAX_WAIT_TIME = 20
ULANG_KOMENTAR = 5
JEDA_ANTAR_ULANGAN = 120


# --- FUNGSI HELPER ---
def wait_for_manual_intervention(driver, message):
    print(f"\n⚠️  {message}")
    print("🖱️  Silakan selesaikan di browser yang terbuka.")
    print("⌨️  Tekan Enter di sini setelah selesai...")
    input()
    print("✅ Melanjutkan proses...")


def check_for_obstacles(driver):
    current_url = driver.current_url.lower()

    obstacles = {
        "captcha": [
            "[data-testid*='captcha']",
            "[aria-label*='captcha']",
            ".captcha",
            "#captcha",
        ],
        "checkpoint": [
            "checkpoint" in current_url,
            "security" in current_url,
            "verify" in current_url,
            "confirm" in current_url,
        ],
        "verification": [
            "[data-testid*='checkpoint']",
            "[data-testid*='security']",
            "[aria-label*='verification']",
            "[aria-label*='verify']",
            "[aria-label*='two-factor']",
            "[aria-label*='2fa']",
        ],
        "blocked": [
            "blocked" in current_url,
            "suspended" in current_url,
            "disabled" in current_url,
        ],
    }

    for obstacle_type, selectors in obstacles.items():
        if obstacle_type in ["checkpoint", "blocked"]:
            if any(
                selector
                for selector in selectors
                if isinstance(selector, bool) and selector
            ):
                return obstacle_type, f"Facebook {obstacle_type.title()}"
        else:
            for selector in selectors:
                if isinstance(selector, str) and driver.find_elements(
                    By.CSS_SELECTOR, selector
                ):
                    return obstacle_type, f"Detected {obstacle_type}"

    return None, None


def handle_verification_prompt(driver):
    print("\n🔐 VERIFIKASI AUTENTIKASI TERDETEKSI!")
    print("📋 Facebook meminta verifikasi tambahan")
    print(f"🌐 URL saat ini: {driver.current_url}")

    verification_types = []
    if (
        "two-factor" in driver.current_url.lower()
        or "2fa" in driver.current_url.lower()
    ):
        verification_types.append("Two-Factor Authentication (2FA)")
    if "checkpoint" in driver.current_url.lower():
        verification_types.append("Security Checkpoint")
    if "verify" in driver.current_url.lower():
        verification_types.append("Account Verification")

    if verification_types:
        print(f"🔍 Jenis verifikasi: {', '.join(verification_types)}")

    print("\n❓ Pilihan:")
    print("1. Selesaikan verifikasi manual (Tekan Y)")
    print("2. Batalkan dan keluar (Tekan N)")

    while True:
        choice = (
            input("Apakah Anda ingin menyelesaikan verifikasi manual? (Y/N): ")
            .strip()
            .upper()
        )
        if choice in ["Y", "N"]:
            return choice == "Y"
        print("❌ Input tidak valid. Ketik Y atau N")


def wait_for_verification_completion(driver, max_wait_minutes=10):
    print(f"⏳ Menunggu verifikasi selesai (maksimal {max_wait_minutes} menit)...")
    print("💡 Tekan Ctrl+C jika ingin membatalkan")

    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60

    while time.time() - start_time < max_wait_seconds:
        try:
            current_url = driver.current_url.lower()

            if (
                "facebook.com" in current_url
                and "checkpoint" not in current_url
                and "security" not in current_url
                and "verify" not in current_url
                and "confirm" not in current_url
            ):

                if (
                    driver.find_elements(
                        By.CSS_SELECTOR,
                        "[data-testid='fb_logo'], [aria-label*='Facebook'], [data-testid='nav-header']",
                    )
                    or current_url.endswith("facebook.com/")
                    or "/home" in current_url
                ):
                    return True

            time.sleep(2)

        except KeyboardInterrupt:
            print("\n❌ Dibatalkan oleh user")
            return False
        except Exception as e:
            print(f"⚠️ Error saat menunggu verifikasi: {e}")
            time.sleep(2)

    print(f"⏰ Timeout {max_wait_minutes} menit tercapai")
    return False


def wait_for_facebook_main_page(driver, max_wait_minutes=10):
    print(f"⏳ Menunggu kembali ke halaman utama Facebook...")
    print("💡 Silakan selesaikan verifikasi di browser")
    print(
        "💡 Tekan Enter di sini setelah verifikasi selesai dan Anda berada di halaman utama Facebook"
    )

    try:
        input("Tekan Enter setelah verifikasi selesai...")

        current_url = driver.current_url.lower()

        is_facebook_main = current_url.startswith(
            "https://www.facebook.com"
        ) and not any(
            [
                "checkpoint" in current_url,
                "security" in current_url,
                "verify" in current_url,
                "confirm" in current_url,
                "auth_platform" in current_url,
                "afad" in current_url,
                "/auth/" in current_url,
                "login" in current_url and "next=" in current_url,
            ]
        )

        if is_facebook_main:
            print(f"✅ Berhasil kembali ke halaman utama Facebook!")
            print(f"🌐 URL sekarang: {driver.current_url}")
            return True
        else:
            print(f"⚠️ Masih belum di halaman utama Facebook")
            print(f"🌐 URL sekarang: {driver.current_url}")

            choice = (
                input("Apakah Anda ingin melanjutkan anyway? (Y/N): ").strip().upper()
            )
            return choice == "Y"

    except KeyboardInterrupt:
        print("\n❌ Dibatalkan oleh user")
        return False
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return False


# --- KODE UTAMA ---
def auto_comment():
    print("Memulai bot auto comment...")

    try:
        chrome_options = Options()

        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")

        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options,
        )

        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})"
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']})"
        )

        print("✅ Driver Chrome berhasil di-setup.")

    except Exception as e:
        print(f"❌ Error saat setup driver: {e}")
        return

    driver.get("https://www.facebook.com")
    wait = WebDriverWait(driver, MAX_WAIT_TIME)
    time.sleep(3)

    try:
        print("Mencoba login otomatis...")

        email_input = wait.until(EC.presence_of_element_located((By.ID, "email")))

        email_input.clear()
        for char in EMAIL_LO:
            email_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        time.sleep(random.uniform(1, 2))

        pass_input = driver.find_element(By.ID, "pass")
        pass_input.clear()
        for char in PASSWORD_LO:
            pass_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        time.sleep(random.uniform(1, 2))

        login_button = driver.find_element(By.NAME, "login")
        login_button.click()

        print("Login request dikirim...")

        captcha_detected = False
        verification_detected = False

        for attempt in range(60):
            try:
                current_url = driver.current_url.lower()

                captcha_elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-testid*='captcha'], [aria-label*='captcha'], .captcha, #captcha",
                )

                verification_indicators = [
                    "checkpoint" in current_url,
                    "security" in current_url,
                    "verify" in current_url,
                    "confirm" in current_url,
                    "authentication" in current_url,
                    "two-factor" in current_url,
                    "2fa" in current_url,
                    "auth_platform" in current_url,
                    "afad" in current_url,
                    "/auth/" in current_url,
                    "/login/" in current_url and "next=" in current_url,
                ]

                verification_elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-testid*='checkpoint'], [data-testid*='security'], [aria-label*='verification'], [aria-label*='verify']",
                )

                is_facebook_main = current_url.startswith(
                    "https://www.facebook.com"
                ) and not any(
                    [
                        "checkpoint" in current_url,
                        "security" in current_url,
                        "verify" in current_url,
                        "confirm" in current_url,
                        "auth_platform" in current_url,
                        "afad" in current_url,
                        "/auth/" in current_url,
                        "login" in current_url and "next=" in current_url,
                    ]
                )

                login_success_elements = driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-testid='fb_logo'], [aria-label*='Facebook'], [data-testid='nav-header'], [data-testid='feed']",
                )

                if captcha_elements:
                    if not captcha_detected:
                        captcha_detected = True
                        print("🔴 CAPTCHA TERDETEKSI!")
                        print("📋 Silakan selesaikan CAPTCHA di browser yang terbuka.")
                        print("⏳ Bot akan menunggu hingga Anda selesai...")

                elif (
                    any(verification_indicators)
                    or verification_elements
                    or not is_facebook_main
                ):
                    if not verification_detected:
                        verification_detected = True

                        print("\n🔐 VERIFIKASI/REDIRECT TERDETEKSI!")
                        print(f"🌐 URL saat ini: {driver.current_url}")

                        if "auth_platform" in current_url or "afad" in current_url:
                            print("🔍 Jenis: Facebook Authentication Platform")
                        elif "checkpoint" in current_url:
                            print("🔍 Jenis: Security Checkpoint")
                        elif "two-factor" in current_url or "2fa" in current_url:
                            print("🔍 Jenis: Two-Factor Authentication")
                        elif "verify" in current_url:
                            print("🔍 Jenis: Account Verification")
                        else:
                            print("🔍 Jenis: Unknown verification/redirect")

                        print("\n❓ Pilihan:")
                        print("1. Selesaikan verifikasi manual (Tekan Y)")
                        print("2. Batalkan dan keluar (Tekan N)")

                        while True:
                            choice = (
                                input(
                                    "Apakah Anda ingin menyelesaikan verifikasi manual? (Y/N): "
                                )
                                .strip()
                                .upper()
                            )
                            if choice in ["Y", "N"]:
                                break
                            print("❌ Input tidak valid. Ketik Y atau N")

                        if choice == "Y":
                            print(
                                "✅ Silakan selesaikan verifikasi di browser yang terbuka"
                            )
                            print("⏳ Bot akan menunggu hingga verifikasi selesai...")
                            print("💡 Tekan Ctrl+C jika ingin membatalkan")

                            if wait_for_facebook_main_page(driver):
                                print("✅ Verifikasi berhasil diselesaikan!")
                                break
                            else:
                                print("❌ Verifikasi gagal atau timeout")
                                print("💡 Mencoba melanjutkan proses...")
                                break
                        else:
                            print("❌ Proses dibatalkan oleh user")
                            driver.quit()
                            return

                elif is_facebook_main and login_success_elements:
                    if captcha_detected:
                        print("✅ CAPTCHA berhasil diselesaikan!")
                    elif verification_detected:
                        print("✅ Verifikasi berhasil diselesaikan!")
                    else:
                        print("✅ Login berhasil!")
                    break

            except Exception as e:
                print(f"⚠️ Error saat cek status login: {e}")

            time.sleep(1)
        else:
            print("⏰ Timeout menunggu login/verifikasi selesai")
            print("💡 Mencoba melanjutkan proses...")

        time.sleep(random.uniform(3, 5))

    except Exception as e:
        print(f"Gagal login. Error: {e}")
        print("💡 Tips: Pastikan akun valid dan selesaikan CAPTCHA jika muncul")
        input("Tekan Enter setelah menyelesaikan masalah di browser...")

    try:
        print(f"Membuka postingan: {URL_POSTINGAN}")
        driver.get(URL_POSTINGAN)
        time.sleep(random.uniform(JEDA_WAKTU, JEDA_WAKTU + 3))
    except Exception as e:
        print(f"Gagal membuka URL postingan. Error: {e}")
        driver.quit()
        return

    wait = WebDriverWait(driver, MAX_WAIT_TIME)

    try:
        print("Mencari kolom komentar...")

        comment_selectors = [
            "div[aria-label*='Tulis komentar']",
            "div[aria-label*='Write a comment']",
            "div[contenteditable='true'][role='textbox']",
            "div[data-testid='fb-comments-composer-input']",
            "div[aria-label*='Comment']",
        ]

        comment_box = None
        for selector in comment_selectors:
            try:
                comment_box = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                print(f"Comment box ditemukan dengan selector: {selector}")
                break
            except:
                continue

        if not comment_box:
            raise Exception(
                "Tidak dapat menemukan kolom komentar dengan semua selector"
            )

        driver.execute_script("arguments[0].scrollIntoView(true);", comment_box)
        time.sleep(2)

        print("Mengirim komentar...")

        for ulangan in range(ULANG_KOMENTAR):
            if ULANG_KOMENTAR > 1:
                print(f"\n🔄 Ulangan ke-{ulangan + 1} dari {ULANG_KOMENTAR}")

            for i, comment_text in enumerate(KOMENTAR_LO):
                try:
                    driver.execute_script("arguments[0].click();", comment_box)
                    time.sleep(random.uniform(1, 2))

                    try:
                        active_element = driver.switch_to.active_element
                        active_element.clear()
                        active_element.send_keys(comment_text)
                    except:
                        comment_box.clear()
                        comment_box.send_keys(comment_text)

                    time.sleep(random.uniform(1, 2))

                    try:
                        active_element = driver.switch_to.active_element
                        active_element.send_keys(Keys.RETURN)
                    except:
                        comment_box.send_keys(Keys.RETURN)

                    print(f"Komentar ke-{i+1} terkirim: '{comment_text}'")

                    if i < len(KOMENTAR_LO) - 1:
                        delay = random.uniform(
                            JEDA_ANTAR_KOMENTAR_MIN, JEDA_ANTAR_KOMENTAR_MAX
                        )
                        print(
                            f"Menunggu {delay:.1f} detik sebelum komentar berikutnya..."
                        )
                        time.sleep(delay)

                except Exception as e:
                    print(f"Gagal mengirim komentar ke-{i+1}: {e}")
                    continue

            if ulangan < ULANG_KOMENTAR - 1:
                print(
                    f"\n⏳ Menunggu {JEDA_ANTAR_ULANGAN} detik sebelum ulangan berikutnya..."
                )
                time.sleep(JEDA_ANTAR_ULANGAN)

    except Exception as e:
        print(f"Gagal menemukan kolom komentar atau mengirim komentar. Error: {e}")
        print(
            "Tips: Facebook sering ganti UI. Pastikan URL postingan benar dan akun memiliki akses."
        )
    finally:
        print("Proses selesai. Menutup browser dalam 10 detik.")
        time.sleep(10)
        driver.quit()


def main():
    print("=" * 60)
    print("🤖 FACEBOOK AUTO COMMENT BOT")
    print("=" * 60)

    print("📋 MODE: Login otomatis")
    print("\n📝 INSTRUKSI:")
    print("1. Pastikan email/password sudah benar")
    print("2. Script akan membuka Chrome otomatis dan login")
    print("3. Jika ada CAPTCHA/Verifikasi, selesaikan manual di browser")
    print("4. Bot akan mendeteksi verifikasi dan memberi pilihan:")
    print("   • Selesaikan manual (Y) - Bot akan menunggu")
    print("   • Batalkan (N) - Bot akan berhenti")
    print("5. Script akan melanjutkan setelah login berhasil")
    print(f"6. Komentar akan diulang {ULANG_KOMENTAR} kali")
    if ULANG_KOMENTAR > 1:
        print(f"   dengan jeda {JEDA_ANTAR_ULANGAN} detik antar ulangan")

    print("\n💡 Chrome akan terbuka otomatis oleh script")
    print("⚠️  Verifikasi yang didukung: 2FA, Security Checkpoint, Account Verification")

    print("\n🚀 Memulai bot...")
    print("-" * 60)

    auto_comment()


if __name__ == "__main__":
    main()

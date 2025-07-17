import os
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

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

EMAIL = os.getenv("FACEBOOK_EMAIL", "")
PASSWORD = os.getenv("FACEBOOK_PASSWORD", "")
KOMENTAR = []
POST_URLS_LIST = []  # Store all URLs to process

# Default comment options
DEFAULT_COMMENTS = [
    "ramaikan",
    "akun murah",
    "gasskan bang",
    "dijamin aman",
    "mantap",
    "up",
    "gas",
    "recommended",
]

JEDA_WAKTU = 5
JEDA_ANTAR_KOMENTAR_MIN = 6
JEDA_ANTAR_KOMENTAR_MAX = 10
MAX_WAIT_TIME = 20
ULANG_KOMENTAR = 1
JEDA_ANTAR_ULANGAN = 120

# Default post URLs for quick selection
DEFAULT_POSTS = [
    "LINK PERTAMA",
    "LINK KEDUA"
]


def get_post_urls():
    """Get Facebook post URLs from user input or default selection"""
    print("\n" + "=" * 60)
    print("🔗 INPUT POSTINGAN FACEBOOK")
    print("=" * 60)

    # Ask user if they want to use default posts or input manually
    print("📋 Pilih metode input postingan:")
    print("1. Gunakan postingan default")
    print("2. Input postingan manual")
    print("3. Gabungan default + manual")

    while True:
        choice = input("Pilih opsi (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("❌ Pilihan tidak valid! Pilih 1, 2, atau 3")

    post_urls = []

    # Option 1: Use default posts
    if choice == "1":
        print(f"\n📋 Postingan default yang tersedia:")
        for i, post in enumerate(DEFAULT_POSTS, 1):
            print(f"   {i}. {post}")

        print(f"\n💡 Pilih postingan (contoh: 1,3,4 atau 'all' untuk semua):")
        selection = input("Pilihan: ").strip().lower()

        if selection == "all":
            post_urls = DEFAULT_POSTS.copy()
            print(f"✅ Menggunakan semua {len(post_urls)} postingan default")
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                post_urls = [
                    DEFAULT_POSTS[i - 1]
                    for i in indices
                    if 1 <= i <= len(DEFAULT_POSTS)
                ]
                print(f"✅ Terpilih {len(post_urls)} postingan default")
            except:
                print("❌ Format pilihan tidak valid, menggunakan postingan pertama")
                post_urls = [DEFAULT_POSTS[0]]

    # Option 2: Manual input only
    elif choice == "2":
        print("📝 Masukkan link postingan Facebook yang ingin dikomentari")
        print("💡 Format link: https://www.facebook.com/groups/namagrup/posts/idpost")
        print("💡 Atau: https://www.facebook.com/username/posts/idpost")
        print("=" * 60)

        post_urls = get_manual_post_input()

    # Option 3: Combination of default and manual
    elif choice == "3":
        # First, select from defaults
        print(f"\n📋 Postingan default yang tersedia:")
        for i, post in enumerate(DEFAULT_POSTS, 1):
            print(f"   {i}. {post}")

        print(f"\n💡 Pilih postingan default (contoh: 1,3 atau kosong untuk skip):")
        selection = input("Pilihan: ").strip()

        if selection:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                post_urls = [
                    DEFAULT_POSTS[i - 1]
                    for i in indices
                    if 1 <= i <= len(DEFAULT_POSTS)
                ]
                print(f"✅ Terpilih {len(post_urls)} postingan default")
            except:
                print("❌ Format pilihan tidak valid, melewati default")
                post_urls = []

        # Then, add manual inputs
        print(
            f"\n📝 Sekarang tambahkan postingan manual (atau ketik 'skip' untuk melewati):"
        )
        manual_posts = get_manual_post_input(allow_skip=True)
        if manual_posts:
            post_urls.extend(manual_posts)

    if not post_urls:
        print("❌ Tidak ada postingan yang dipilih!")
        return None

    print(f"\n✅ Total {len(post_urls)} postingan Facebook siap untuk dikomentari:")
    for i, post in enumerate(post_urls, 1):
        display_url = post[:70] + "..." if len(post) > 70 else post
        print(f"   {i}. {display_url}")

    return post_urls


def get_manual_post_input(allow_skip=False):
    """Helper function for manual post input"""
    post_urls = []

    while True:
        print(f"\n📍 Postingan ke-{len(post_urls) + 1}:")
        if allow_skip and len(post_urls) == 0:
            url = input(
                "Masukkan link postingan Facebook (atau 'skip' untuk melewati): "
            ).strip()
            if url.lower() == "skip":
                break
        else:
            url = input("Masukkan link postingan Facebook: ").strip()

        if not url:
            if len(post_urls) == 0:
                print("⚠️ Minimal harus ada 1 postingan!")
                continue
            else:
                break

        # Basic validation for Facebook post URL
        if "facebook.com" not in url:
            print("⚠️ Link harus berupa link postingan Facebook yang valid!")
            print("   Format: https://www.facebook.com/.../posts/...")
            continue

        post_urls.append(url)
        print(f"✅ Postingan ditambahkan: {url[:50]}{'...' if len(url) > 50 else ''}")

        # Ask if user wants to add more posts
        print(f"\n📊 Total postingan yang sudah ditambahkan: {len(post_urls)}")
        add_more = input("❓ Ingin menambah postingan lagi? (y/n): ").lower().strip()

        if add_more not in ["y", "yes", "ya"]:
            break

    return post_urls


def get_user_input():
    """Get user input for posting URL and comments"""
    global KOMENTAR, EMAIL, PASSWORD

    print("=" * 60)
    print("📝 SETUP KONFIGURASI AUTO COMMENT")
    print("=" * 60)

    # Get credentials if not in .env
    if not EMAIL:
        EMAIL = input("Masukkan email Facebook: ").strip()
    if not PASSWORD:
        PASSWORD = input("Masukkan password Facebook: ").strip()

    if not EMAIL or not PASSWORD:
        print("❌ Email dan password diperlukan!")
        return False

    # Get post URLs
    post_urls = get_post_urls()
    if not post_urls:
        return False

    # Store all post URLs for processing
    global POST_URLS_LIST
    POST_URLS_LIST = post_urls

    print(f"\n✅ Total {len(POST_URLS_LIST)} postingan akan diproses:")
    for i, url in enumerate(POST_URLS_LIST, 1):
        display_url = url[:50] + "..." if len(url) > 50 else url
        print(f"   {i}. {display_url}")

    # Get comments
    print(f"\n💬 SETUP KOMENTAR:")
    print("Pilih metode input komentar:")
    print("1. Gunakan komentar default")
    print("2. Masukkan komentar custom")
    print("3. Gabungan default dan custom")

    choice = input("Pilih opsi (1/2/3): ").strip()

    if choice == "1":
        KOMENTAR = DEFAULT_COMMENTS.copy()
        print(f"✅ Menggunakan {len(KOMENTAR)} komentar default")

    elif choice == "2":
        print("\n📝 Masukkan komentar Anda (ketik 'selesai' jika sudah selesai):")
        KOMENTAR = []
        while True:
            comment = input("Komentar: ").strip()
            if comment.lower() == "selesai":
                break
            if comment:
                KOMENTAR.append(comment)
                print(f"  ✅ Ditambahkan: {comment}")

    elif choice == "3":
        print("\n📝 Komentar default yang tersedia:")
        for i, comment in enumerate(DEFAULT_COMMENTS, 1):
            print(f"  {i}. {comment}")

        print(
            "\nMasukkan nomor komentar yang ingin digunakan (contoh: 1,3,5) atau 'semua' untuk semua:"
        )
        selection = input("Pilihan: ").strip()

        if selection.lower() == "semua":
            KOMENTAR = DEFAULT_COMMENTS.copy()
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(",")]
                KOMENTAR = [
                    DEFAULT_COMMENTS[i]
                    for i in indices
                    if 0 <= i < len(DEFAULT_COMMENTS)
                ]
            except:
                print("❌ Pilihan tidak valid, menggunakan semua komentar default")
                KOMENTAR = DEFAULT_COMMENTS.copy()

        print(f"\n✅ Terpilih {len(KOMENTAR)} komentar")

        # Option to add custom comments
        add_custom = input("Tambahkan komentar custom? (y/n): ").lower().strip()
        if add_custom in ["y", "yes", "ya"]:
            print("Masukkan komentar tambahan (ketik 'selesai' jika sudah selesai):")
            while True:
                comment = input("Komentar: ").strip()
                if comment.lower() == "selesai":
                    break
                if comment:
                    KOMENTAR.append(comment)
                    print(f"  ✅ Ditambahkan: {comment}")

    if not KOMENTAR:
        print("❌ Minimal diperlukan satu komentar!")
        return False

    # Get repeat settings
    global ULANG_KOMENTAR, JEDA_ANTAR_ULANGAN
    print(f"\n🔄 PENGATURAN PENGULANGAN:")
    print(
        f"Pengaturan saat ini: Ulang {ULANG_KOMENTAR} kali dengan jeda {JEDA_ANTAR_ULANGAN} detik"
    )
    change_repeat = input("Ubah pengaturan pengulangan? (y/n): ").lower().strip()

    if change_repeat in ["y", "yes", "ya"]:
        try:
            ULANG_KOMENTAR = int(input("Jumlah pengulangan (1-10): "))
            if ULANG_KOMENTAR < 1 or ULANG_KOMENTAR > 10:
                ULANG_KOMENTAR = 1

            if ULANG_KOMENTAR > 1:
                JEDA_ANTAR_ULANGAN = int(input("Jeda antar pengulangan (detik): "))
        except:
            print("⚠️  Menggunakan pengaturan pengulangan default")

    # Summary
    print(f"\n📋 RINGKASAN:")
    print(f"Email: {EMAIL}")
    print(f"Postingan: {len(POST_URLS_LIST)} postingan akan diproses")
    print(f"Komentar: {len(KOMENTAR)} item")
    print(f"Pengulangan: {ULANG_KOMENTAR} kali")
    if ULANG_KOMENTAR > 1:
        print(f"Jeda antar pengulangan: {JEDA_ANTAR_ULANGAN} detik")

    print(f"\nKomentar yang akan diposting:")
    for i, comment in enumerate(KOMENTAR, 1):
        print(f"  {i}. {comment}")

    confirm = input("\nLanjutkan dengan pengaturan ini? (y/n): ").lower().strip()
    return confirm in ["y", "yes", "ya"]


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
    if not get_user_input():
        print("❌ Setup dibatalkan atau input tidak valid")
        return

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
        for char in EMAIL:
            email_input.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
        time.sleep(random.uniform(1, 2))

        pass_input = driver.find_element(By.ID, "pass")
        pass_input.clear()
        for char in PASSWORD:
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

    # Process all posts
    successful_posts = 0
    total_posts = len(POST_URLS_LIST)

    print(f"\n🚀 Memulai pemrosesan {total_posts} postingan...")
    print("=" * 60)

    for post_index, post_url in enumerate(POST_URLS_LIST, 1):
        print(f"\n📍 POSTINGAN {post_index}/{total_posts}")
        print(f"🔗 URL: {post_url}")
        print("-" * 40)

        try:
            print(f"Membuka postingan...")
            driver.get(post_url)
            time.sleep(random.uniform(JEDA_WAKTU, JEDA_WAKTU + 3))

            # Process comments for this post
            if process_comments_for_post(driver, post_url, post_index):
                successful_posts += 1
                print(f"✅ Postingan {post_index} berhasil diproses!")
            else:
                print(f"❌ Postingan {post_index} gagal diproses!")

            # Wait between posts (except for the last one)
            if post_index < total_posts:
                wait_time = random.uniform(30, 60)  # Wait 30-60 seconds between posts
                print(
                    f"⏳ Menunggu {wait_time:.1f} detik sebelum postingan berikutnya..."
                )
                time.sleep(wait_time)

        except Exception as e:
            print(f"❌ Error pada postingan {post_index}: {e}")
            continue

    # Final summary
    print("\n" + "=" * 60)
    print("📊 RINGKASAN AKHIR")
    print("=" * 60)
    print(f"✅ Postingan berhasil: {successful_posts}/{total_posts}")
    print(f"❌ Postingan gagal: {total_posts - successful_posts}/{total_posts}")

    if successful_posts == total_posts:
        print("🎉 Semua postingan berhasil diproses!")
    elif successful_posts > 0:
        print("⚠️ Sebagian postingan berhasil diproses")
    else:
        print("😞 Tidak ada postingan yang berhasil diproses")

    print("Proses selesai. Menutup browser dalam 10 detik.")
    time.sleep(10)
    driver.quit()


def process_comments_for_post(driver, post_url, post_number):
    """Process comments for a single post"""
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
                break
            except:
                continue

        if not comment_box:
            print("❌ Tidak dapat menemukan kolom komentar")
            return False

        driver.execute_script("arguments[0].scrollIntoView(true);", comment_box)
        time.sleep(2)

        print("Mengirim komentar...")

        for ulangan in range(ULANG_KOMENTAR):
            if ULANG_KOMENTAR > 1:
                print(f"🔄 Ulangan ke-{ulangan + 1} dari {ULANG_KOMENTAR}")

            for i, comment_text in enumerate(KOMENTAR):
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

                    print(f"✅ Komentar ke-{i+1}: '{comment_text}'")

                    if i < len(KOMENTAR) - 1:
                        delay = random.uniform(
                            JEDA_ANTAR_KOMENTAR_MIN, JEDA_ANTAR_KOMENTAR_MAX
                        )
                        print(f"⏳ Menunggu {delay:.1f} detik...")
                        time.sleep(delay)

                except Exception as e:
                    print(f"❌ Gagal mengirim komentar ke-{i+1}: {e}")
                    continue

            if ulangan < ULANG_KOMENTAR - 1:
                print(
                    f"⏳ Menunggu {JEDA_ANTAR_ULANGAN} detik sebelum ulangan berikutnya..."
                )
                time.sleep(JEDA_ANTAR_ULANGAN)

        return True

    except Exception as e:
        print(f"❌ Error pada postingan {post_number}: {e}")
        return False


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

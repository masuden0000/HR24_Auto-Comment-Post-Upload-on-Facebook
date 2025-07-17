import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_credentials():
    """Get Facebook credentials from environment variables"""
    email = os.getenv("FACEBOOK_EMAIL")
    password = os.getenv("FACEBOOK_PASSWORD")

    if not email or not password:
        print("❌ Kredensial Facebook tidak ditemukan di file .env!")
        print(
            "Pastikan FACEBOOK_EMAIL dan FACEBOOK_PASSWORD sudah diatur di file .env Anda"
        )
        return None, None

    return email, password


# Default group URLs for quick selection
DEFAULT_GROUPS = [
    "LINK PERTAMA",
    "LINK KEDUA",
]


def get_group_links():
    """Get Facebook group links from user input or default selection"""
    print("\n" + "=" * 60)
    print("🔗 INPUT GRUP FACEBOOK")
    print("=" * 60)

    # Ask user if they want to use default groups or input manually
    print("📋 Pilih metode input grup:")
    print("1. Gunakan grup default")
    print("2. Input grup manual")
    print("3. Gabungan default + manual")

    while True:
        choice = input("Pilih opsi (1/2/3): ").strip()
        if choice in ["1", "2", "3"]:
            break
        print("❌ Pilihan tidak valid! Pilih 1, 2, atau 3")

    groups_links_list = []

    # Option 1: Use default groups
    if choice == "1":
        print(f"\n📋 Grup default yang tersedia:")
        for i, group in enumerate(DEFAULT_GROUPS, 1):
            # Extract group name from URL for better display
            group_name = (
                group.split("/groups/")[1].rstrip("/") if "/groups/" in group else group
            )
            print(f"   {i}. {group_name}")
            print(f"      {group}")

        print(f"\n💡 Pilih grup (contoh: 1,3,5 atau 'all' untuk semua):")
        selection = input("Pilihan: ").strip().lower()

        if selection == "all":
            groups_links_list = DEFAULT_GROUPS.copy()
            print(f"✅ Menggunakan semua {len(groups_links_list)} grup default")
        else:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                groups_links_list = [
                    DEFAULT_GROUPS[i - 1]
                    for i in indices
                    if 1 <= i <= len(DEFAULT_GROUPS)
                ]
                print(f"✅ Terpilih {len(groups_links_list)} grup default")
            except:
                print("❌ Format pilihan tidak valid, menggunakan grup pertama")
                groups_links_list = [DEFAULT_GROUPS[0]]

    # Option 2: Manual input only
    elif choice == "2":
        print("📝 Masukkan link grup Facebook yang akan dituju")
        print("💡 Format link: https://www.facebook.com/groups/namagrup")
        print("💡 Pastikan Anda sudah menjadi member grup tersebut")
        print("=" * 60)

        groups_links_list = get_manual_group_input()

    # Option 3: Combination of default and manual
    elif choice == "3":
        # First, select from defaults
        print(f"\n📋 Grup default yang tersedia:")
        for i, group in enumerate(DEFAULT_GROUPS, 1):
            group_name = (
                group.split("/groups/")[1].rstrip("/") if "/groups/" in group else group
            )
            print(f"   {i}. {group_name}")
            print(f"      {group}")

        print(f"\n💡 Pilih grup default (contoh: 1,3 atau kosong untuk skip):")
        selection = input("Pilihan: ").strip()

        if selection:
            try:
                indices = [int(x.strip()) for x in selection.split(",")]
                groups_links_list = [
                    DEFAULT_GROUPS[i - 1]
                    for i in indices
                    if 1 <= i <= len(DEFAULT_GROUPS)
                ]
                print(f"✅ Terpilih {len(groups_links_list)} grup default")
            except:
                print("❌ Format pilihan tidak valid, melewati default")
                groups_links_list = []

        # Then, add manual inputs
        print(
            f"\n📝 Sekarang tambahkan grup manual (atau ketik 'skip' untuk melewati):"
        )
        manual_groups = get_manual_group_input(allow_skip=True)
        if manual_groups:
            groups_links_list.extend(manual_groups)

    if not groups_links_list:
        print("❌ Tidak ada grup yang dipilih!")
        return None

    print(f"\n✅ Total {len(groups_links_list)} grup Facebook siap untuk posting:")
    for i, group in enumerate(groups_links_list, 1):
        # Extract and display group name nicely
        group_name = (
            group.split("/groups/")[1].rstrip("/") if "/groups/" in group else "Unknown"
        )
        print(f"   {i}. {group_name}")

    # Safety check for too many groups
    if len(groups_links_list) > 10:
        print(f"\n⚠️ Anda memilih {len(groups_links_list)} grup (lebih dari 10)")
        confirm = (
            input("Ini mungkin dianggap spam oleh Facebook. Lanjutkan? (y/n): ")
            .lower()
            .strip()
        )
        if confirm not in ["y", "yes", "ya"]:
            print("❌ Dibatalkan oleh user")
            return None

    return groups_links_list


def get_manual_group_input(allow_skip=False):
    """Helper function for manual group input"""
    groups_links_list = []

    while True:
        print(f"\n📍 Grup ke-{len(groups_links_list)+1}:")
        if allow_skip and len(groups_links_list) == 0:
            group_link = input(
                "Masukkan link grup Facebook (atau 'skip' untuk melewati): "
            ).strip()
            if group_link.lower() == "skip":
                break
        else:
            group_link = input("Masukkan link grup Facebook: ").strip()

        if not group_link:
            if len(groups_links_list) == 0:
                print("⚠️ Minimal harus ada 1 grup!")
                continue
            else:
                break

        # Basic validation for Facebook group URL
        if not group_link.startswith("https://www.facebook.com/groups/"):
            print("⚠️ Link harus berupa link grup Facebook yang valid!")
            print("   Format: https://www.facebook.com/groups/namagrup")
            continue

        groups_links_list.append(group_link)
        # Extract group name for display
        group_name = (
            group_link.split("/groups/")[1].rstrip("/")
            if "/groups/" in group_link
            else "Unknown"
        )
        print(f"✅ Grup ditambahkan: {group_name}")

        print(f"\n📊 Total grup yang sudah ditambahkan: {len(groups_links_list)}")

        # Safety warning for many groups
        if len(groups_links_list) >= 5:
            print(
                f"⚠️ Anda sudah menambah {len(groups_links_list)} grup. Terlalu banyak grup mungkin dianggap spam."
            )

        if len(groups_links_list) >= 10:
            print("🛑 Maksimal 10 grup untuk keamanan. Berhenti menambah grup.")
            break

        add_more = input("❓ Ingin menambah grup lagi? (y/n): ").lower().strip()
        if add_more not in ["y", "yes", "ya"]:
            break

    return groups_links_list


def get_message():
    """Get message for posting from user input"""
    print("\n" + "=" * 60)
    print("💬 INPUT PESAN POSTING")
    print("=" * 60)

    while True:
        message = input("Masukkan pesan yang akan diposting: ").strip()

        if not message:
            print("⚠️ Pesan tidak boleh kosong!")
            continue

        print(f"\n📝 Preview pesan:")
        print(f"'{message}'")

        confirm = input("\n❓ Apakah pesan sudah benar? (y/n): ").lower().strip()
        if confirm in ["y", "yes", "ya"]:
            return message
        else:
            print("📝 Silakan masukkan pesan yang baru:")


def get_image_paths():
    """Get image paths from user input"""
    print("\n" + "=" * 60)
    print("🖼️ INPUT GAMBAR")
    print("=" * 60)
    print("📝 Masukkan path gambar yang akan diupload")
    print("💡 Gunakan path absolut (lengkap)")
    print("💡 Format yang didukung: .png, .jpg, .jpeg, .gif, .bmp")
    print("=" * 60)

    images_list = []
    while True:
        print(f"\n📷 Gambar ke-{len(images_list)+1}:")
        path = input("Masukkan path gambar: ").strip()

        if not path:
            if len(images_list) == 0:
                print("⚠️ Minimal harus ada 1 gambar!")
                continue
            else:
                break

        # Remove quotes if user added them
        path = path.strip('"').strip("'")

        # Check if file exists
        if not os.path.exists(path):
            print(f"❌ File tidak ditemukan: {path}")
            continue

        # Check if it's an image file
        valid_extensions = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]
        if not any(path.lower().endswith(ext) for ext in valid_extensions):
            print(f"❌ Format file tidak didukung: {path}")
            print(f"   Format yang didukung: {', '.join(valid_extensions)}")
            continue

        # Check file size
        file_size = os.path.getsize(path) / (1024 * 1024)  # MB
        if file_size > 50:
            print(f"❌ File terlalu besar ({file_size:.1f}MB). Maksimal 50MB")
            continue

        images_list.append(path)
        print(f"✅ Gambar ditambahkan: {os.path.basename(path)} ({file_size:.1f}MB)")

        # Ask if user wants to add more images
        print(f"\n📊 Total gambar yang sudah ditambahkan: {len(images_list)}")
        add_more = input("❓ Ingin menambah gambar lagi? (y/n): ").lower().strip()

        if add_more not in ["y", "yes", "ya"]:
            break

    if not images_list:
        print("❌ Tidak ada gambar yang ditambahkan!")
        return None

    print(f"\n✅ Total {len(images_list)} gambar siap untuk upload:")
    for i, img in enumerate(images_list, 1):
        print(f"   {i}. {os.path.basename(img)}")

    return images_list


def main():
    print("=" * 60)
    print("🤖 FACEBOOK AUTO POSTER")
    print("=" * 60)
    print("📝 Script untuk posting otomatis ke grup Facebook")
    print("⚠️  Pastikan Anda sudah menjadi member dari grup yang dituju")
    print("=" * 60)

    # Get credentials from .env file
    account, password = get_credentials()
    if not account or not password:
        return

    # Get group links from user input
    groups_links_list = get_group_links()
    if not groups_links_list:
        return

    # Get message from user input
    message = get_message()
    if not message:
        return

    # Get image paths from user input
    images_list = get_image_paths()
    if not images_list:
        return

    driver = None  # Initialize driver variable
    try:
        # Setup Chrome options
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.default_content_setting_values.notifications": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Initialize driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Login to Facebook
        driver.get("https://www.facebook.com")
        time.sleep(3)
        emailelement = driver.find_element(By.ID, "email")
        emailelement.send_keys(account)

        passelement = driver.find_element(By.ID, "pass")
        passelement.send_keys(password)

        loginelement = driver.find_element(By.NAME, "login")
        loginelement.click()

        # Wait for login
        time.sleep(10)

        # Check if redirected properly to Facebook home page
        current_url = driver.current_url

        # Check if still on login page or redirected to security check
        needs_verification = (
            "login" in current_url.lower()
            or "checkpoint" in current_url.lower()
            or "security" in current_url.lower()
            or "two_step_verification" in current_url.lower()
            or "authentication" in current_url.lower()
            or not current_url.startswith("https://www.facebook.com/")
        )

        if needs_verification:
            print("\n⚠️  DETEKSI AUTENTIKASI TAMBAHAN DIPERLUKAN!")
            print("Tampaknya Facebook meminta verifikasi keamanan tambahan.")
            print("\nSilakan lakukan hal berikut:")
            print("1. Lihat browser Chrome yang terbuka")
            print("2. Selesaikan verifikasi keamanan (OTP, captcha, dll) secara manual")
            print("3. Pastikan Anda sudah masuk ke halaman utama Facebook")
            print("4. Tekan ENTER di terminal ini untuk melanjutkan script")

            input("\nTekan ENTER setelah verifikasi selesai...")

            # Check again after manual verification
            current_url = driver.current_url

            if "login" in current_url.lower() or "checkpoint" in current_url.lower():
                print(
                    "❌ Verifikasi belum selesai atau gagal login. Menghentikan script."
                )
                return

        print("✅ Login berhasil diselesaikan")

        # Ask user if they want to proceed with posting
        print(
            f"\n📝 Siap untuk memulai posting ke {len(groups_links_list)} grup Facebook:"
        )
        for i, group in enumerate(groups_links_list, 1):
            print(f"  {i}. {group}")
        print(f"\nPesan yang akan diposting: '{message}'")
        print(f"Gambar yang akan diupload: {len(images_list)} file")

        proceed = (
            input("\nApakah Anda ingin melanjutkan proses posting? (y/n): ")
            .lower()
            .strip()
        )
        if proceed not in ["y", "yes", "ya"]:
            print("❌ Posting dibatalkan oleh user.")
            return

        # Validasi file gambar sebelum upload
        valid_images = []
        print("🔍 Memvalidasi file gambar...")
        for img_path in images_list:
            if os.path.exists(img_path):
                file_size = os.path.getsize(img_path) / (1024 * 1024)  # MB
                if file_size < 50:  # Facebook limit ~50MB
                    valid_images.append(img_path)
                    print(f"  ✅ Valid: {img_path.split('\\')[-1]} ({file_size:.1f}MB)")
                else:
                    print(
                        f"  ❌ Terlalu besar: {img_path.split('\\')[-1]} ({file_size:.1f}MB)"
                    )
            else:
                print(f"  ❌ File tidak ditemukan: {img_path}")

        if not valid_images:
            print("❌ Tidak ada gambar valid untuk diupload")
            return
        else:
            images_list = valid_images  # Update dengan file yang valid
            print(f"📸 Siap upload {len(images_list)} gambar valid")

        # Post on each group
        for i, group in enumerate(groups_links_list, 1):
            print(f"Memproses grup {i}: {group}")
            driver.get(group)
            time.sleep(5)

            try:
                # STEP 1: Cari dan klik area posting utama
                post_area_found = False
                print(f"🔍 Mencari area posting untuk grup {i}...")

                selectors = [
                    (
                        '//span[contains(text(), "Tulis sesuatu")]/../..',
                        "Tulis sesuatu text",
                    ),
                ]

                post_container = None
                for selector, desc in selectors:
                    try:
                        post_box = driver.find_element(By.XPATH, selector)
                        post_box.click()
                        time.sleep(3)

                        post_container = post_box
                        post_area_found = True
                        break
                    except Exception as e:
                        continue

                if not post_area_found:
                    print(f"❌ Tidak dapat menemukan area posting untuk grup {i}")
                    continue

                # STEP 2: Tunggu composer terbuka sepenuhnya, lalu input text
                time.sleep(2)
                print("📝 Menulis pesan...")

                try:
                    # Cari text area di dalam composer yang sudah terbuka
                    text_selectors = [
                        '//div[@role="textbox" and @contenteditable="true"]',
                        '//div[@data-testid="status-attachment-mentions-input"]',
                        '//div[contains(@aria-label, "What") and @contenteditable="true"]',
                        '//div[contains(@aria-label, "Tulis") and @contenteditable="true"]',
                        '//div[@contenteditable="true"]',
                    ]

                    text_input = None
                    for text_selector in text_selectors:
                        try:
                            text_elements = driver.find_elements(
                                By.XPATH, text_selector
                            )
                            if text_elements:
                                text_input = text_elements[-1]
                                break
                        except:
                            continue

                    if text_input:
                        text_input.clear()
                        text_input.send_keys(message)
                        time.sleep(2)

                except Exception as e:
                    print(f"  ❌ Error menulis pesan: {e}")

                # STEP 3: Upload gambar di composer yang SAMA
                photo_uploaded = False
                print("📸 Mencoba upload gambar di composer yang sama...")

                try:
                    # Cari input file di dalam composer yang sudah terbuka
                    # Gunakan context yang lebih spesifik
                    time.sleep(1)

                    # Method 1: Cari input file yang ada tanpa klik tombol tambahan
                    file_inputs = driver.find_elements(
                        By.CSS_SELECTOR, 'input[type="file"]'
                    )

                    if file_inputs:
                        print(f"  🔍 Ditemukan {len(file_inputs)} input file")

                        # Pilih input file yang terakhir (biasanya yang terkait dengan composer aktif)
                        file_input = file_inputs[-1]

                        try:
                            accept_attr = file_input.get_attribute("accept")
                            print(f"    Accept attribute: {accept_attr}")

                            if (
                                not accept_attr
                                or "image" in accept_attr.lower()
                                or "*" in accept_attr
                            ):
                                all_photos = "\n".join(images_list)

                                # Pastikan input visible
                                driver.execute_script(
                                    """
                                    arguments[0].style.display = 'block';
                                    arguments[0].style.visibility = 'visible';
                                    arguments[0].style.opacity = '1';
                                    arguments[0].style.position = 'static';
                                """,
                                    file_input,
                                )

                                file_input.send_keys(all_photos)
                                time.sleep(4)  # Tunggu upload selesai

                                # Verifikasi upload dengan mencari preview
                                preview_elements = driver.find_elements(
                                    By.CSS_SELECTOR,
                                    'img[src*="blob:"], img[src*="data:image"]',
                                )

                                if preview_elements:
                                    photo_uploaded = True
                                    print(
                                        f"  ✅ Upload berhasil: {len(preview_elements)} preview ditemukan"
                                    )
                                else:
                                    print(
                                        "  ⚠️  Upload tidak menampilkan preview, tapi mungkin berhasil"
                                    )
                                    photo_uploaded = True  # Assume success

                        except Exception as e:
                            print(f"  ❌ Error upload: {e}")

                    # Method 2: Jika belum berhasil, cari tombol foto dalam composer aktif
                    if not photo_uploaded:
                        print("  🔄 Mencari tombol foto dalam composer aktif...")

                        # Cari tombol foto/video dalam area composer yang sudah terbuka
                        photo_button_selectors = [
                            '//div[contains(@aria-label, "Foto/video")][@role="button"]',
                            '//div[contains(@aria-label, "Photo/video")][@role="button"]',
                            '//div[@role="button" and contains(text(), "Foto")]',
                            # Selector yang lebih spesifik untuk composer aktif
                            '//div[@role="dialog"]//div[contains(@aria-label, "Foto")]',
                            '//div[contains(@class, "composer")]//div[contains(@aria-label, "Foto")]',
                        ]

                        photo_button = None
                        for selector in photo_button_selectors:
                            try:
                                buttons = driver.find_elements(By.XPATH, selector)
                                if buttons:
                                    # Coba ambil yang terlihat dan bisa diklik
                                    for btn in buttons:
                                        if btn.is_displayed() and btn.is_enabled():
                                            photo_button = btn
                                            print(
                                                f"  🔍 Ditemukan tombol foto: {selector}"
                                            )
                                            break
                                    if photo_button:
                                        break
                            except:
                                continue

                        if photo_button:
                            photo_button.click()
                            time.sleep(2)

                            # Setelah klik, cari input file yang baru muncul
                            new_file_inputs = driver.find_elements(
                                By.CSS_SELECTOR, 'input[type="file"]'
                            )
                            if new_file_inputs:
                                latest_input = new_file_inputs[-1]
                                all_photos = "\n".join(images_list)
                                latest_input.send_keys(all_photos)
                                time.sleep(3)
                                photo_uploaded = True
                                print(
                                    f"  ✅ Upload via tombol berhasil: {len(images_list)} gambar"
                                )

                    # Method 3: JavaScript fallback dalam konteks yang sama
                    if not photo_uploaded:
                        print("  🔄 JavaScript fallback untuk upload...")
                        try:
                            js_upload = """
                            // Cari input file terakhir (yang paling relevan)
                            var inputs = document.querySelectorAll('input[type="file"]');
                            if (inputs.length > 0) {
                                var input = inputs[inputs.length - 1];
                                var files = arguments[0];
                                var fileList = [];
                                
                                files.forEach(function(path) {
                                    var fileName = path.split('\\\\').pop() || path.split('/').pop();
                                    var file = new File([''], fileName, {type: 'image/png'});
                                    fileList.push(file);
                                });
                                
                                var dt = new DataTransfer();
                                fileList.forEach(file => dt.items.add(file));
                                input.files = dt.files;
                                
                                // Trigger events
                                input.dispatchEvent(new Event('change', {bubbles: true}));
                                return true;
                            }
                            return false;
                            """

                            result = driver.execute_script(js_upload, images_list)
                            if result:
                                time.sleep(3)
                                photo_uploaded = True
                                print(f"  ✅ JavaScript upload berhasil")

                        except Exception as e:
                            print(f"  ❌ JavaScript upload error: {e}")

                    if not photo_uploaded:
                        manual_upload = (
                            input("  Upload gambar manual? (y/n): ").lower().strip()
                        )
                        if manual_upload in ["y", "yes", "ya"]:
                            print("  📝 Upload gambar manual di browser")
                            input("  Tekan ENTER setelah selesai...")
                            photo_uploaded = True

                except Exception as e:
                    print(f"  ❌ Error upload gambar: {e}")

                # STEP 4: Posting dengan konteks yang sama
                time.sleep(3)
                print("🎯 Mencari tombol Post dalam composer aktif...")

                # Cari tombol post dalam composer yang sudah terbuka
                post_buttons = [
                    (
                        "//div[@aria-label='Posting'][@role='button']",
                        "Posting aria-label",
                    ),
                    (
                        "//div[contains(@aria-label, 'Posting')][@role='button']",
                        "Posting contains",
                    ),
                    (
                        "//div[@role='button' and .//span[contains(text(), 'Posting')]]",
                        "Button dengan text Posting",
                    ),
                    # Lebih spesifik untuk composer aktif
                    (
                        "//div[@role='dialog']//div[@aria-label='Posting']",
                        "Dialog Posting",
                    ),
                    (
                        "//div[@role='dialog']//button[contains(text(), 'Posting')]",
                        "Dialog Button Posting",
                    ),
                ]

                posted = False
                for button_xpath, desc in post_buttons:
                    try:
                        print(f"  🔍 Mencoba: {desc}")
                        post_buttons_found = driver.find_elements(
                            By.XPATH, button_xpath
                        )

                        for post_button in post_buttons_found:
                            if post_button.is_displayed() and post_button.is_enabled():
                                # Cek apakah tombol tidak disabled
                                is_disabled = post_button.get_attribute("aria-disabled")
                                if is_disabled != "true":
                                    post_button.click()
                                    posted = True
                                    print(f"  ✅ Berhasil posting dengan: {desc}")
                                    break

                        if posted:
                            break

                    except Exception as e:
                        print(f"  ❌ Gagal dengan {desc}: {str(e)[:50]}...")
                        continue

                if not posted:
                    manual_post = input("Posting manual? (y/n): ").lower().strip()
                    if manual_post in ["y", "yes", "ya"]:
                        print("📝 Klik tombol Post manual di browser")
                        input("Tekan ENTER setelah selesai...")
                else:
                    print(f"🎉 Berhasil posting ke grup {i}!")

                time.sleep(5)

            except Exception as e:
                print(f"❌ Error memproses grup {i}: {e}")
                continue

        print("\n🎉 Selesai memproses semua grup Facebook!")
        print("📊 Ringkasan:")
        print(f"   - Total grup yang diproses: {len(groups_links_list)}")
        print("   - Periksa hasil posting di browser jika ada yang berhasil")

        # Option to keep browser open for manual verification
        keep_open = (
            input("\nIngin membiarkan browser tetap terbuka untuk verifikasi? (y/n): ")
            .lower()
            .strip()
        )
        if keep_open in ["y", "yes", "ya"]:
            print(
                "🌐 Browser akan tetap terbuka. Tutup secara manual jika sudah selesai."
            )
            input("Tekan ENTER untuk menutup browser dan mengakhiri script...")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if driver is not None:
            driver.quit()
            print("🚫 Browser ditutup")


if __name__ == "__main__":
    main()

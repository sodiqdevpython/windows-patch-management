import win32com.client


def list_pending_patches():
    session = win32com.client.Dispatch("Microsoft.Update.Session")
    searcher = session.CreateUpdateSearcher()
    result = searcher.Search("IsInstalled=0 and Type='Software'")

    updates_info = {}

    if result.Updates.Count == 0:
        print("[-] Hali o'rnatilmagan yangi Windows patch topilmadi.")
    else:
        print(f"[+] {result.Updates.Count} ta hali o'rnatilmagan yangi Windows patchlar topildi:\n")
        for i in range(result.Updates.Count):
            update = result.Updates.Item(i)
            update_id = update.Identity.UpdateID
            print(f"update_id:{update_id}")
            print(f"title:{update.Title}")
            print(f"kb:{list(update.KBArticleIDs) if update.KBArticleIDs else 'Yo‘q'}")
            print(f"Mandatory:{update.IsMandatory}")
            print(f"reboot_reuqired:{update.RebootRequired}")
            print(f"downloaded:{update.IsDownloaded}")
            print(f"support:{update.SupportUrl}")
            print("-" * 60)

            updates_info[update_id] = update

    return updates_info


def download_patch(update):
    updates_to_download = win32com.client.Dispatch("Microsoft.Update.UpdateColl")
    updates_to_download.Add(update)
    downloader = win32com.client.Dispatch("Microsoft.Update.Downloader")
    downloader.Updates = updates_to_download

    print(f"[+] Yuklab olinayabdi: {update.Title}")
    result = downloader.Download()
    if result.ResultCode == 2:
        print("[+] Yuklab olish tugadi.")
    else:
        print(f"[-] Yuklab olish muvaffaqiyatsiz, kod: {result.ResultCode}, xato: {result}")


def install_patch(update):
    updates_to_install = win32com.client.Dispatch("Microsoft.Update.UpdateColl")
    updates_to_install.Add(update)
    installer = win32com.client.Dispatch("Microsoft.Update.Installer")
    installer.Updates = updates_to_install

    print(f"[+] O'rnatilmoqda: {update.Title}")
    result = installer.Install()

    if result.ResultCode == 2:
        print("[+] Patch muvaffaqiyatli o'rnatildi.")
    else:
        print(f"[-] O'rnatishda muammo, kod: {result.ResultCode} natija: {result}")

    print(f"[+] Reboot kerak: {result.RebootRequired}")


if __name__ == "__main__":
    updates = list_pending_patches()

    if updates:
        # Qaysi ID ni yuklashni tanlash
        a = input("ID (download): ").strip()
        if a in updates:
            download_patch(updates[a])
        else:
            print("[-] Bunday ID topilmadi.")

        # Qaysi ID ni o‘rnatishni tanlash
        b = input("ID (install): ").strip()
        if b in updates:
            install_patch(updates[b])
        else:
            print("[-] Bunday ID topilmadi.")

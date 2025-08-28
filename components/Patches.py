import win32com.client
import pythoncom
from .GetBios import get_windows_bios_uuid

def list_pending_patches():
    pythoncom.CoInitialize()
    try:
        session = win32com.client.Dispatch("Microsoft.Update.Session")
        searcher = session.CreateUpdateSearcher()
        result = searcher.Search("IsInstalled=0 and Type='Software'")

        updates_info = []

        if result.Updates.Count == 0:
            print("[-] Hali o'rnatilmagan yangi Windows patch topilmadi.")
        else:
            print(f"[+] {result.Updates.Count} ta hali o'rnatilmagan yangi Windows patchlar topildi:\n")
            for i in range(result.Updates.Count):
                update = result.Updates.Item(i)
                update_id = update.Identity.UpdateID
                patch_info = {
                    "title": update.Title,
                    "support": update.SupportUrl,
                    "kb": list(update.KBArticleIDs) if update.KBArticleIDs else "Yo‘q",
                    "mandatory": bool(update.IsMandatory),
                    "reboot_required": bool(update.RebootRequired),
                    "downloaded": bool(update.IsDownloaded),
                    "device_bios_uuid": get_windows_bios_uuid()
                }
                print(f"Topildi: {patch_info}")
                updates_info.append(patch_info)

        return updates_info

    finally:
        pythoncom.CoUninitialize()


def download_patch(update):
    pythoncom.CoInitialize()
    try:
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

    finally:
        pythoncom.CoUninitialize()


def install_patch(update):
    pythoncom.CoInitialize()
    try:
        updates_to_install = win32com.client.Dispatch("Microsoft.Update.UpdateColl")
        updates_to_install.Add(update)
        installer = win32com.client.Dispatch("Microsoft.Update.Installer")
        installer.Updates = updates_to_install

        print(f"[+] O'rnatilayabdi: {update.Title}")
        result = installer.Install()

        if result.ResultCode == 2:
            print("[+] Patch o'rnatildi.")
        else:
            print(f"[-] O'rnatishda muammo, kod: {result.ResultCode}, natija: {result}")

        print(f"[+] Reboot kerak: {result.RebootRequired}")

    finally:
        pythoncom.CoUninitialize()
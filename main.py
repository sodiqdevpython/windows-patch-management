import win32com.client

def check_pending_patches():
    session = win32com.client.Dispatch("Microsoft.Update.Session")
    searcher = session.CreateUpdateSearcher()
    result = searcher.Search("IsInstalled=0 and Type='Software'")

    if result.Updates.Count == 0:
        print("[-] Hali o‘rnatilmagan Windows patch topilmadi.")
    else:
        print(f"[+] {result.Updates.Count} ta hali o‘rnatilmagan Windows patch topildi:\n")
        for i in range(result.Updates.Count):
            update = result.Updates.Item(i)
            print(f"Title       : {update.Title}")
            print(f"KB Article  : {list(update.KBArticleIDs) if update.KBArticleIDs else 'Yo‘q'}")
            print(f"Critical    : {update.IsMandatory}")
            print(f"Downloaded  : {update.IsDownloaded}")
            print(f"Support URL : {update.SupportUrl}")
            print("-" * 60)

check_pending_patches()

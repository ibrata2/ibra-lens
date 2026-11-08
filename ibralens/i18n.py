"""لغة البرنامج: العربي (الافتراضي) أو الإنكليزي — مستقلة عن لغة الوندوز."""

_LANG = "ar"


def set_lang(lang):
    global _LANG
    _LANG = "en" if lang == "en" else "ar"


def lang():
    return _LANG


def is_rtl():
    return _LANG == "ar"


def T(s):
    if _LANG == "ar":
        return s
    return EN.get(s, s)


EN = {
    "برمجة و تطوير ابراهيم الخزرجي": "Developed by Ibrahim Al-Khazraji",
    "بايت": "B",
    "اكتب شنو تريد تلكى…  مثل: طفل، وشم، سيارة، بحر، ورد": "Describe what you're looking for…  e.g. child, tattoo, car, sea, flowers",
    "بحث": "Search",
    "🖼  بحث بصورة": "🖼  Search by image",
    "ارفع صورة أو اسحبها هنا حتى يلكي مثيلها بالحاسبة": "Upload or drop an image here to find its matches on this PC",
    "✕ إلغاء": "✕ Clear",
    "اختار صورة": "Choose an image",
    "صور (*.jpg *.jpeg *.png *.webp *.bmp *.gif *.tif *.tiff *.heic *.jfif)": "Images (*.jpg *.jpeg *.png *.webp *.bmp *.gif *.tif *.tiff *.heic *.jfif)",
    "فتح الصورة": "Open image",
    "📁 فتح مكانها": "📁 Open file location",
    "نسخ المسار": "Copy path",
    "نسخ الصورة": "Copy image",
    "🔎 بحث عن صور مشابهة": "🔎 Find similar images",
    "الصور المكررة": "Duplicate images",
    "متشابهة (تشمل المصغرة والمضغوطة ونسخ الواتساب)": "Similar (includes resized, compressed and WhatsApp copies)",
    "متطابقة تماماً فقط (نفس الملف)": "Exact copies only (same file)",
    "ابحث عن المكرر": "Find duplicates",
    "🗑 حذف المحدد إلى سلة المحذوفات": "🗑 Move selected to Recycle Bin",
    "عرض المزيد": "Show more",
    "جاري البحث عن المكرر…": "Searching for duplicates…",
    "الفهرسة": "Indexing",
    "+ إضافة مجلد": "+ Add folder",
    "حذف المحدد": "Remove selected",
    "▶ ابدأ الفهرسة": "▶ Start indexing",
    "⏸ إيقاف مؤقت": "⏸ Pause",
    "⏹ إيقاف": "⏹ Stop",
    "إعادة بناء الفهرس من الصفر": "Rebuild index from scratch",
    "اختار مجلد": "Choose a folder",
    "الإعدادات": "Settings",
    "استخدم كارت الشاشة (أسرع) — يتطبق بعد إعادة التشغيل": "Use the graphics card (faster) — applies after restart",
    "حدّث الفهرس تلقائياً عند فتح البرنامج": "Update the index automatically on startup",
    "بلغني إذا نزل إصدار جديد من البرنامج": "Notify me when a new version is released",
    "حفظ": "Save",
    "فحص التحديثات": "Check for updates",
    "انحفظت الإعدادات.": "Settings saved.",
    "البحث الذكي عن الصور": "Smart image search",
    "جاري تحميل الذكاء الاصطناعي…": "Loading AI models…",
    "عدد النتائج:": "Results:",
    "الذكاء الاصطناعي بعده يتحمّل… لحظات": "AI is still loading… one moment",
    "البحث عن مثيل:": "Finding matches for:",
    "ما لكيت نتائج": "No results found",
    "📁 مكانها": "📁 Location",
    "تعذر العرض": "Can't preview",
    "لازم تفهرس الصور أول (صفحة الفهرسة).": "Index your images first (Indexing page).",
    "ماكو صور مكررة 👌": "No duplicates found 👌",
    "البرنامج يمر على الأماكن المحددة ويحفظ بصمة لكل صورة. أول مرة تاخذ وقت، ": "The app scans the selected places and stores a fingerprint for each image. The first run takes a while; ",
    "وبعدها يحدّث بس الصور الجديدة والمعدلة.": "after that it only updates new and changed images.",
    "<b>أماكن البحث</b>": "<b>Search locations</b>",
    "الذكاء الاصطناعي بعده يتحمّل… جرب بعد لحظات.": "AI is still loading… try again in a moment.",
    "حدد مكان واحد على الأقل.": "Select at least one location.",
    "تمسح الفهرس الحالي وتبدي من جديد؟": "Delete the current index and start over?",
    "تجاهل الصور الأصغر من (KB):": "Ignore images smaller than (KB):",
    "تجاهل الصور اللي أصغر ضلع بيها أقل من (بكسل) — الأيقونات:": "Ignore images whose shortest side is under (px) — icons:",
    "دقة كشف المتشابهة (أقل = أدق، أكثر = يلكي تعديلات أكبر):": "Similar-image tolerance (lower = stricter, higher = catches bigger edits):",
    "تليكرام t.me/ibraprogram": "Telegram t.me/ibraprogram",
    "تيك توك @ibraprogram": "TikTok @ibraprogram",
    "ملفات الذكاء الاصطناعي ناقصة — أعد تنصيب البرنامج.": "AI model files are missing — please reinstall the app.",
    "بدأت الفهرسة…": "Indexing started…",
    "⬆ تحديث إلى": "⬆ Update to",
    "⬆ إعادة محاولة التحديث": "⬆ Retry update",
    "مطابقة": "Match",
    "<div>البرنامج يفهم شنو موجود داخل الصورة — عربي أو إنكليزي</div>": "<div>The app understands what's inside each image — in Arabic or English</div>",
    "بعد ما فهرسنا الصور.</div><div>روح لصفحة <b>الفهرسة</b> واضغط <b>ابدأ الفهرسة</b> أول مرة.</div>": "Your images aren't indexed yet.</div><div>Go to <b>Indexing</b> and press <b>Start indexing</b> the first time.</div>",
    "نتائج «{q}» — {n} صورة ({t} ث)": "Results for “{q}” — {n} images ({t} s)",
    "ما كدرت أفتح هاي الصورة.": "Couldn't open this image.",
    "{a} مطابقة • {n} نتيجة مرتبة من الأقرب ({t} ث)": "{a} exact • {n} results, closest first ({t} s)",
    "🗑 حذف ({n}) إلى سلة المحذوفات": "🗑 Move ({n}) to Recycle Bin",
    "<b>مجموعة {n}</b> — {c} صور • {kind} • توفير {w}": "<b>Group {n}</b> — {c} images • {kind} • saves {w}",
    "الأفضل — نخليها": "Best — keep",
    "حذف": "Delete",
    "انحذفت {n} صورة.": "{n} images deleted.",
    "▶ استئناف": "▶ Resume",
    "بالفهرس: {n} صورة • {s} • المعالج: {d}": "Indexed: {n} images • {s} • Processor: {d}",
    "🔎  البحث": "🔎  Search",
    "🧬  الصور المكررة": "🧬  Duplicates",
    "📂  الفهرسة": "📂  Indexing",
    "⚙  الإعدادات وحول": "⚙  Settings && About",
    "جاهز • {d} • بالفهرس {n} صورة": "Ready • {d} • {n} images indexed",
    "تحديث الفهرس:": "Updating index:",
    "تنزله وتنصبه هسه؟": "Download and install it now?",
    "مشابهة {p}%": "Similar {p}%",
    "<div style='font-size:18px;font-weight:700;color:#fff'>اكتب وصف الصورة أو اسحب صورة هنا</div>": "<div style='font-size:18px;font-weight:700;color:#fff'>Describe an image or drop a picture here</div>",
    "تنقل {n} صورة لسلة المحذوفات؟": "Move {n} images to the Recycle Bin?",
    "متطابقة تماماً": "exact copies",
    "متشابهة": "similar",
    "{g} مجموعة • {n} نسخة زايدة • تكدر توفر {w}": "{g} groups • {n} extra copies • you can free {w}",
    "تنقل {n} صورة مكررة لسلة المحذوفات؟\n(تكدر ترجعها من السلة إذا احتجتها)": "Move {n} duplicate images to the Recycle Bin?\n(You can restore them from the Recycle Bin if needed)",
    "القرص": "Drive",
    "🔍 جاري البحث عن الصور… لكيت {f} صورة ({t} جديدة/معدلة) • {d} مجلد": "🔍 Scanning… found {f} images ({t} new/changed) • {d} folders",
    "تعذر تشغيل الذكاء الاصطناعي:": "Couldn't start the AI engine:",
    "نزل إصدار جديد": "New version available",
    "قريبة جداً {p}%": "Very close {p}%",
    " • باقي تقريباً {m} د {s} ث": " • about {m} min {s} s left",
    "🧠 فهرسة {d} / {t} • {r} صورة/ث{eta} • صغيرة متروكة {s} • تالفة {e}": "🧠 Indexing {d} / {t} • {r} img/s{eta} • small skipped {s} • broken {e}",
    "الإصدار {v} — البحث الذكي عن الصور": "Version {v} — Smart image search",
    "جاري التنزيل {v}%": "Downloading {v}%",
    "فحص الملفات… {n} صورة": "Scanning files… {n} images",
    "عندك آخر إصدار 👍": "You have the latest version 👍",
    "ما كدرت أتصل بالإنترنت لفحص التحديثات.": "Couldn't connect to check for updates.",
    " • جديد {n} • محذوف من الحاسبة {r}": " • new {n} • removed from PC {r}",
    "✅ خلصت الفهرسة": "✅ Indexing finished",
    "⏹ توقفت الفهرسة": "⏹ Indexing stopped",
    "لغة البرنامج:": "App language:",
    "تتغير اللغة بعد إعادة تشغيل البرنامج. تعيد التشغيل هسه؟": "The language changes after restarting the app. Restart now?",
}

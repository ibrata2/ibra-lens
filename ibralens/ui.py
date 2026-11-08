"""واجهة IBRA LENS — عربي، زجاجي أسود وأحمر."""
import os
import subprocess
import sys
import threading
import time
from collections import OrderedDict

from PySide6.QtCore import (Qt, QSize, QRect, QRectF, Signal, QObject, QRunnable, QThreadPool,
                            QAbstractListModel, QModelIndex, QTimer, QUrl, QPoint)
from PySide6.QtGui import (QIcon, QPixmap, QImage, QPainter, QColor, QFont, QPainterPath, QAction,
                           QDesktopServices, QLinearGradient, QPen, QFontMetrics)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QListView, QStyledItemDelegate, QStackedWidget,
                               QFileDialog, QMenu, QMessageBox, QProgressBar, QCheckBox, QSpinBox,
                               QComboBox, QScrollArea, QFrame, QListWidget, QListWidgetItem, QSlider,
                               QAbstractItemView, QSizePolicy, QStyle, QGridLayout, QButtonGroup)

from . import updater
from .db import DB
from .dupes import find_duplicates
from .engine import create_engine, models_present, open_image
from .indexer import Indexer, list_drives
from .paths import APP_NAME, VERSION, asset, data_dir
from .settings import Settings
from .i18n import T, set_lang, is_rtl, lang


def DIR():
    return Qt.RightToLeft if is_rtl() else Qt.LeftToRight


def restart_app():
    from PySide6.QtCore import QProcess
    if getattr(sys, "frozen", False):
        QProcess.startDetached(sys.executable, [])
    else:
        QProcess.startDetached(sys.executable, [os.path.abspath(sys.argv[0])])
    QApplication.quit()


ACCENT = "#ff3b48"
CREDIT = "برمجة و تطوير ابراهيم الخزرجي"
TELEGRAM = "https://t.me/ibraprogram"
TIKTOK = "https://www.tiktok.com/@ibraprogram"

QSS = f"""
* {{ font-family: 'Segoe UI', 'Tahoma', 'Noto Sans Arabic', sans-serif; font-size: 14px; color: #f2f2f5; }}
QMainWindow, #root {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0b0b10, stop:0.55 #140c10, stop:1 #24090e); }}
#side {{ background: rgba(255,255,255,0.04); border-left: 1px solid rgba(255,255,255,0.08); }}
#brand {{ font-size: 20px; font-weight: 800; letter-spacing: 1px; }}
#sub {{ color: #a9a9b5; font-size: 12px; }}
QPushButton {{ background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.14);
              border-radius: 12px; padding: 9px 16px; }}
QPushButton:hover {{ background: rgba(255,255,255,0.13); }}
QPushButton:pressed {{ background: rgba(255,59,72,0.35); }}
QPushButton:disabled {{ color: #6d6d78; }}
QPushButton#primary {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ff4b57, stop:1 #b3101d);
                       border: 1px solid rgba(255,255,255,0.25); font-weight: 700; }}
QPushButton#primary:hover {{ background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ff6670, stop:1 #c8182a); }}
QPushButton#nav {{ text-align: %ALIGN%; padding: 12px 18px; border-radius: 12px; background: transparent;
                   border: 1px solid transparent; font-size: 15px; }}
QPushButton#nav:hover {{ background: rgba(255,255,255,0.07); }}
QPushButton#nav:checked {{ background: rgba(255,59,72,0.22); border: 1px solid rgba(255,59,72,0.55); font-weight: 700; }}
QLineEdit, QSpinBox, QComboBox {{ background: rgba(0,0,0,0.35); border: 1px solid rgba(255,255,255,0.16);
              border-radius: 12px; padding: 9px 12px; selection-background-color: {ACCENT}; }}
QLineEdit:focus {{ border: 1px solid {ACCENT}; }}
QLineEdit#search {{ font-size: 17px; padding: 12px 16px; border-radius: 16px; }}
QComboBox QAbstractItemView {{ background: #1b1b22; border: 1px solid #333; selection-background-color: {ACCENT}; }}
#card {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.10); border-radius: 18px; }}
#title {{ font-size: 22px; font-weight: 800; }}
#hint {{ color: #a9a9b5; }}
#banner {{ background: rgba(255,59,72,0.18); border: 1px solid rgba(255,59,72,0.5); border-radius: 12px; }}
QListView, QListWidget {{ background: transparent; border: none; outline: none; }}
QListWidget::item {{ padding: 6px; border-radius: 8px; }}
QListWidget::item:selected {{ background: rgba(255,59,72,0.25); }}
QProgressBar {{ background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.12); border-radius: 9px;
               text-align: center; height: 18px; }}
QProgressBar::chunk {{ border-radius: 8px; background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #ff4b57, stop:1 #b3101d); }}
QScrollBar:vertical {{ background: transparent; width: 10px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: rgba(255,255,255,0.18); border-radius: 4px; min-height: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: rgba(255,255,255,0.18); border-radius: 4px; min-width: 30px; }}
QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.35);
                        background: rgba(0,0,0,0.3); }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border: 1px solid #ff8a92; }}
QMenu {{ background: #18181f; border: 1px solid #34343f; border-radius: 10px; padding: 6px; }}
QMenu::item {{ padding: 8px 22px; border-radius: 6px; }}
QMenu::item:selected {{ background: rgba(255,59,72,0.35); }}
QToolTip {{ background: #18181f; border: 1px solid #34343f; color: #fff; padding: 6px; }}
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QSlider::groove:horizontal {{ height: 6px; background: rgba(255,255,255,0.15); border-radius: 3px; }}
QSlider::handle:horizontal {{ width: 16px; margin: -6px 0; border-radius: 8px; background: {ACCENT}; }}
QStatusBar {{ background: rgba(0,0,0,0.3); color: #b9b9c4; }}
"""


def human_size(n):
    n = float(n or 0)
    for u in ("بايت", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.0f} {T(u)}" if u == "بايت" else f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} PB"


def open_location(path):
    if sys.platform == "win32":
        subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    else:
        QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(path)))


def open_file(path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))


def to_trash(paths):
    from send2trash import send2trash
    ok = []
    for p in paths:
        try:
            send2trash(os.path.normpath(p))
            ok.append(p)
        except Exception:
            pass
    return ok


# ====================================================================== thumbnails
class _ThumbSig(QObject):
    ready = Signal(str, QImage)


class _ThumbJob(QRunnable):
    def __init__(self, path, size, sig):
        super().__init__()
        self.path, self.size, self.sig = path, size, sig

    def run(self):
        img = QImage()
        try:
            im = open_image(self.path, max_side=self.size * 2)
            im.thumbnail((self.size * 2, self.size * 2))
            data = im.convert("RGBA").tobytes("raw", "RGBA")
            img = QImage(data, im.width, im.height, QImage.Format_RGBA8888).copy()
        except Exception:
            pass
        self.sig.ready.emit(self.path, img)


class Thumbs(QObject):
    updated = Signal(str)

    def __init__(self, size=200):
        super().__init__()
        self.size = size
        self.cache = OrderedDict()
        self.pending = set()
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(max(2, min(6, os.cpu_count() or 4)))
        self.sig = _ThumbSig()
        self.sig.ready.connect(self._done)

    def get(self, path):
        pm = self.cache.get(path)
        if pm is not None:
            self.cache.move_to_end(path)
            return pm
        if path not in self.pending:
            self.pending.add(path)
            self.pool.start(_ThumbJob(path, self.size, self.sig))
        return None

    def _done(self, path, img):
        self.pending.discard(path)
        self.cache[path] = QPixmap.fromImage(img) if not img.isNull() else QPixmap()
        while len(self.cache) > 1500:
            self.cache.popitem(last=False)
        self.updated.emit(path)


# ====================================================================== results grid
class ResultModel(QAbstractListModel):
    def __init__(self, thumbs):
        super().__init__()
        self.items = []
        self.thumbs = thumbs
        self.row_of = {}
        thumbs.updated.connect(self._thumb_ready)

    def set_items(self, items):
        self.beginResetModel()
        self.items = items
        self.row_of = {d["path"]: i for i, d in enumerate(items)}
        self.endResetModel()

    def remove_paths(self, paths):
        ps = set(paths)
        self.set_items([d for d in self.items if d["path"] not in ps])

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        d = self.items[index.row()]
        if role == Qt.UserRole:
            return d
        if role == Qt.ToolTipRole:
            return f"{d['path']}\n{d.get('w')}×{d.get('h')} • {human_size(d.get('size'))}"
        return None

    def _thumb_ready(self, path):
        r = self.row_of.get(path)
        if r is not None:
            ix = self.index(r)
            self.dataChanged.emit(ix, ix)


class CardDelegate(QStyledItemDelegate):
    W, H = 196, 236

    def __init__(self, thumbs, mode_fn):
        super().__init__()
        self.thumbs = thumbs
        self.mode_fn = mode_fn

    def sizeHint(self, opt, index):
        return QSize(self.W, self.H)

    def paint(self, p, opt, index):
        d = index.data(Qt.UserRole)
        r = opt.rect.adjusted(6, 6, -6, -6)
        p.save()
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        sel = bool(opt.state & QStyle.State_Selected)
        hov = bool(opt.state & QStyle.State_MouseOver)
        path = QPainterPath()
        path.addRoundedRect(QRectF(r), 14, 14)
        p.fillPath(path, QColor(255, 59, 72, 60) if sel else QColor(255, 255, 255, 22 if hov else 13))
        p.setPen(QPen(QColor(255, 59, 72, 200) if sel else QColor(255, 255, 255, 30), 1.2))
        p.drawPath(path)

        tr = QRect(r.x() + 8, r.y() + 8, r.width() - 16, r.width() - 16)
        clip = QPainterPath()
        clip.addRoundedRect(QRectF(tr), 10, 10)
        p.fillPath(clip, QColor(0, 0, 0, 90))
        pm = self.thumbs.get(d["path"])
        if pm is not None and not pm.isNull():
            s = pm.size().scaled(tr.size(), Qt.KeepAspectRatio)
            tgt = QRect(tr.x() + (tr.width() - s.width()) // 2, tr.y() + (tr.height() - s.height()) // 2,
                        s.width(), s.height())
            p.setClipPath(clip)
            p.drawPixmap(tgt, pm)
            p.setClipping(False)
        elif pm is not None:
            p.setPen(QColor("#777"))
            p.drawText(tr, Qt.AlignCenter, T("تعذر العرض"))

        # شارة النسبة
        sc = d.get("score")
        if sc is not None:
            label, col = self.badge(sc)
            f = QFont(p.font())
            f.setPointSizeF(8.5)
            f.setBold(True)
            p.setFont(f)
            fm = QFontMetrics(f)
            bw = fm.horizontalAdvance(label) + 14
            br = QRect(tr.right() - bw - 6, tr.y() + 6, bw, 22)
            bp = QPainterPath()
            bp.addRoundedRect(QRectF(br), 11, 11)
            p.fillPath(bp, QColor(col))
            p.setPen(QColor("white"))
            p.drawText(br, Qt.AlignCenter, label)

        f = QFont(p.font())
        f.setPointSizeF(9)
        f.setBold(False)
        p.setFont(f)
        p.setPen(QColor("#e9e9ee"))
        name = os.path.basename(d["path"])
        nr = QRect(r.x() + 10, tr.bottom() + 6, r.width() - 20, 20)
        p.drawText(nr, Qt.AlignCenter, QFontMetrics(f).elidedText(name, Qt.ElideMiddle, nr.width()))
        p.setPen(QColor("#9a9aa6"))
        f.setPointSizeF(8)
        p.setFont(f)
        info = f"{d.get('w')}×{d.get('h')}  •  {human_size(d.get('size'))}"
        p.drawText(QRect(r.x() + 10, nr.bottom() + 1, r.width() - 20, 18), Qt.AlignCenter, info)
        p.restore()

    def badge(self, sc):
        if self.mode_fn() == "image":
            if sc >= 0.965:
                return T("مطابقة"), "#1f9d55"
            if sc >= 0.88:
                return T("قريبة جداً {p}%").format(p=f"{sc*100:.0f}"), "#c27c0e"
            return T("مشابهة {p}%").format(p=f"{sc*100:.0f}"), "#b3101d"
        pct = max(1, min(99, int((sc - 0.12) / 0.22 * 100)))
        return f"{pct}%", "#b3101d"


class ResultsView(QListView):
    def __init__(self, thumbs, mode_fn):
        super().__init__()
        self.setViewMode(QListView.IconMode)
        self.setResizeMode(QListView.Adjust)
        self.setMovement(QListView.Static)
        self.setUniformItemSizes(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setMouseTracking(True)
        self.setSpacing(2)
        self.setLayoutDirection(DIR())
        self.model_ = ResultModel(thumbs)
        self.setModel(self.model_)
        self.setItemDelegate(CardDelegate(thumbs, mode_fn))
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.verticalScrollBar().setSingleStep(30)

    def selected(self):
        return [ix.data(Qt.UserRole) for ix in self.selectedIndexes()]


# ====================================================================== pages
def card():
    f = QFrame()
    f.setObjectName("card")
    return f


class SearchPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.win = win
        self.mode = "text"
        self.query_image = None
        self.setAcceptDrops(True)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 12)
        lay.setSpacing(12)

        top = QHBoxLayout()
        self.q = QLineEdit()
        self.q.setObjectName("search")
        self.q.setPlaceholderText(T("اكتب شنو تريد تلكى…  مثل: طفل، وشم، سيارة، بحر، ورد"))
        self.q.returnPressed.connect(self.do_text)
        b = QPushButton(T("بحث"))
        b.setObjectName("primary")
        b.clicked.connect(self.do_text)
        bi = QPushButton(T("🖼  بحث بصورة"))
        bi.clicked.connect(self.pick_image)
        bi.setToolTip(T("ارفع صورة أو اسحبها هنا حتى يلكي مثيلها بالحاسبة"))
        top.addWidget(self.q, 1)
        top.addWidget(b)
        top.addWidget(bi)
        lay.addLayout(top)

        # شريط الصورة المرفوعة
        self.qbar = QFrame()
        self.qbar.setObjectName("banner")
        qb = QHBoxLayout(self.qbar)
        qb.setContentsMargins(10, 6, 10, 6)
        self.qthumb = QLabel()
        self.qthumb.setFixedSize(54, 54)
        self.qlabel = QLabel()
        x = QPushButton(T("✕ إلغاء"))
        x.clicked.connect(self.clear_image)
        qb.addWidget(self.qthumb)
        qb.addWidget(self.qlabel, 1)
        qb.addWidget(x)
        self.qbar.hide()
        lay.addWidget(self.qbar)

        row = QHBoxLayout()
        self.info = QLabel("")
        self.info.setObjectName("hint")
        row.addWidget(self.info, 1)
        row.addWidget(QLabel(T("عدد النتائج:")))
        self.count = QComboBox()
        for n in (100, 300, 600, 1000):
            self.count.addItem(str(n), n)
        self.count.setCurrentIndex(max(0, self.count.findData(win.s.get("results", 300))))
        self.count.currentIndexChanged.connect(self.rerun)
        row.addWidget(self.count)
        lay.addLayout(row)

        self.stack = QStackedWidget()
        self.empty = QLabel()
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setObjectName("hint")
        self.empty.setWordWrap(True)
        self.view = ResultsView(win.thumbs, lambda: self.mode)
        self.view.doubleClicked.connect(lambda ix: open_file(ix.data(Qt.UserRole)["path"]))
        self.view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.view.customContextMenuRequested.connect(self.menu)
        self.stack.addWidget(self.empty)
        self.stack.addWidget(self.view)
        lay.addWidget(self.stack, 1)
        self.show_empty()

    def show_empty(self, text=None):
        self.empty.setText(text or (
            "<div style='font-size:42px'>🔎</div>" +
            T("<div style='font-size:18px;font-weight:700;color:#fff'>اكتب وصف الصورة أو اسحب صورة هنا</div>") +
            T("<div>البرنامج يفهم شنو موجود داخل الصورة — عربي أو إنكليزي</div>")))
        self.stack.setCurrentIndex(0)

    # -------------------------------------------------- drag & drop
    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls() or e.mimeData().hasImage():
            e.acceptProposedAction()

    def dropEvent(self, e):
        md = e.mimeData()
        if md.hasUrls():
            for u in md.urls():
                if u.isLocalFile():
                    self.search_image(u.toLocalFile())
                    return
        if md.hasImage():
            img = QImage(md.imageData())
            p = os.path.join(data_dir(), "dropped.png")
            img.save(p)
            self.search_image(p)

    # -------------------------------------------------- actions
    def pick_image(self):
        p, _ = QFileDialog.getOpenFileName(self, T("اختار صورة"), "",
                                           T("صور (*.jpg *.jpeg *.png *.webp *.bmp *.gif *.tif *.tiff *.heic *.jfif)"))
        if p:
            self.search_image(p)

    def clear_image(self):
        self.query_image = None
        self.qbar.hide()
        self.mode = "text"
        self.view.model_.set_items([])
        self.show_empty()

    def rerun(self):
        self.win.s["results"] = self.count.currentData()
        self.win.s.save()
        if self.mode == "image" and self.query_image:
            self.search_image(self.query_image)
        elif self.q.text().strip():
            self.do_text()

    def ready(self):
        if self.win.engine is None:
            self.info.setText(T("الذكاء الاصطناعي بعده يتحمّل… لحظات"))
            return False
        if self.win.db.count() == 0:
            self.show_empty("<div style='font-size:42px'>📂</div><div style='font-size:17px;color:#fff'>" +
                            T("بعد ما فهرسنا الصور.</div><div>روح لصفحة <b>الفهرسة</b> واضغط <b>ابدأ الفهرسة</b> أول مرة.</div>"))
            return False
        return True

    def do_text(self):
        q = self.q.text().strip()
        if not q or not self.ready():
            return
        self.mode = "text"
        self.query_image = None
        self.qbar.hide()
        t = time.time()
        vec = self.win.engine.embed_text(q)
        res = self.win.db.search(vec, top=self.count.currentData())
        self.show_results(res, T("نتائج «{q}» — {n} صورة ({t} ث)").format(q=q, n=len(res), t=f"{time.time()-t:.2f}"))

    def search_image(self, path):
        if not self.ready():
            return
        try:
            im = open_image(path, max_side=1024)
        except Exception:
            QMessageBox.warning(self, APP_NAME, T("ما كدرت أفتح هاي الصورة."))
            return
        self.mode = "image"
        self.query_image = path
        pm = QPixmap(path)
        if pm.isNull():
            data = im.convert("RGBA")
            pm = QPixmap.fromImage(QImage(data.tobytes("raw", "RGBA"), data.width, data.height,
                                          QImage.Format_RGBA8888).copy())
        self.qthumb.setPixmap(pm.scaled(54, 54, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.qlabel.setText(T("البحث عن مثيل:") + f" <b>{os.path.basename(path)}</b>")
        self.qbar.show()
        t = time.time()
        vec = self.win.engine.embed_image(im)
        res = self.win.db.search(vec, top=self.count.currentData())
        same = sum(1 for d in res if d["score"] >= 0.965)
        self.show_results(res, T("{a} مطابقة • {n} نتيجة مرتبة من الأقرب ({t} ث)").format(a=same, n=len(res), t=f"{time.time()-t:.2f}"))

    def show_results(self, res, msg):
        self.view.model_.set_items(res)
        self.view.scrollToTop()
        self.info.setText(msg)
        if res:
            self.stack.setCurrentIndex(1)
        else:
            self.show_empty(T("ما لكيت نتائج"))

    def menu(self, pos):
        sel = self.view.selected()
        if not sel:
            return
        d = sel[0]
        m = QMenu(self)
        m.setLayoutDirection(DIR())
        m.addAction(T("فتح الصورة"), lambda: open_file(d["path"]))
        m.addAction(T("📁 فتح مكانها"), lambda: open_location(d["path"]))
        m.addAction(T("نسخ المسار"), lambda: QApplication.clipboard().setText("\n".join(x["path"] for x in sel)))
        m.addAction(T("نسخ الصورة"), lambda: QApplication.clipboard().setImage(QImage(d["path"])))
        m.addAction(T("🔎 بحث عن صور مشابهة"), lambda: self.search_image(d["path"]))
        m.addSeparator()
        m.addAction(T("🗑 حذف ({n}) إلى سلة المحذوفات").format(n=len(sel)), lambda: self.delete(sel))
        m.exec(self.view.viewport().mapToGlobal(pos))

    def delete(self, sel):
        if QMessageBox.question(self, APP_NAME, T("تنقل {n} صورة لسلة المحذوفات؟").format(n=len(sel))) != QMessageBox.Yes:
            return
        ok = to_trash([d["path"] for d in sel])
        self.win.db.remove_paths(ok)
        self.view.model_.remove_paths(ok)


# ---------------------------------------------------------------------- duplicates
class DupGroup(QFrame):
    def __init__(self, page, g, n):
        super().__init__()
        self.setObjectName("card")
        self.page = page
        self.items = g["items"]
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        hdr = QHBoxLayout()
        allexact = all(d["exact"] for d in self.items)
        t = QLabel(T("<b>مجموعة {n}</b> — {c} صور • {kind} • توفير {w}").format(
            n=n, c=len(self.items), kind=T("متطابقة تماماً") if allexact else T("متشابهة"), w=human_size(g['waste'])))
        hdr.addWidget(t, 1)
        lay.addLayout(hdr)
        sc = QScrollArea()
        sc.setWidgetResizable(True)
        sc.setFixedHeight(232)
        sc.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sc.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        row = QHBoxLayout(inner)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        self.checks = []
        self.thumbs = []
        for i, d in enumerate(self.items):
            w = QFrame()
            w.setFixedWidth(176)
            v = QVBoxLayout(w)
            v.setContentsMargins(0, 0, 0, 0)
            v.setSpacing(3)
            th = QLabel()
            th.setFixedSize(176, 132)
            th.setAlignment(Qt.AlignCenter)
            th.setStyleSheet("background: rgba(0,0,0,0.35); border-radius: 10px;")
            th.setCursor(Qt.PointingHandCursor)
            th.mouseDoubleClickEvent = lambda e, p=d["path"]: open_file(p)
            th.setToolTip(d["path"])
            v.addWidget(th)
            self.thumbs.append((th, d["path"]))
            cb = QCheckBox(T("الأفضل — نخليها") if i == 0 else T("حذف"))
            cb.setChecked(i != 0)
            self.checks.append(cb)
            v.addWidget(cb)
            nm = QLabel(f"{d['w']}×{d['h']} • {human_size(d['size'])}")
            nm.setObjectName("hint")
            v.addWidget(nm)
            loc = QPushButton(T("📁 مكانها"))
            loc.setStyleSheet("padding: 4px 8px; border-radius: 8px; font-size: 12px;")
            loc.setToolTip(d["path"])
            loc.clicked.connect(lambda _=False, p=d["path"]: open_location(p))
            v.addWidget(loc)
            row.addWidget(w)
        row.addStretch(1)
        sc.setWidget(inner)
        lay.addWidget(sc)
        page.win.thumbs.updated.connect(self._thumb)
        for th, p in self.thumbs:
            pm = page.win.thumbs.get(p)
            if pm is not None:
                self._set(th, pm)

    def _set(self, th, pm):
        if not pm.isNull():
            th.setPixmap(pm.scaled(th.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            th.setText(T("تعذر العرض"))

    def _thumb(self, path):
        for th, p in self.thumbs:
            if p == path:
                pm = self.page.win.thumbs.cache.get(p)
                if pm is not None:
                    self._set(th, pm)

    def marked(self):
        return [d["path"] for d, cb in zip(self.items, self.checks) if cb.isChecked()]


class DupPage(QWidget):
    PAGE = 40

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.groups = []
        self.shown = 0
        self.widgets = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 12)
        lay.setSpacing(12)
        t = QLabel(T("الصور المكررة"))
        t.setObjectName("title")
        lay.addWidget(t)
        row = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItem(T("متشابهة (تشمل المصغرة والمضغوطة ونسخ الواتساب)"), "similar")
        self.mode.addItem(T("متطابقة تماماً فقط (نفس الملف)"), "exact")
        row.addWidget(self.mode, 1)
        b = QPushButton(T("ابحث عن المكرر"))
        b.setObjectName("primary")
        b.clicked.connect(self.run)
        row.addWidget(b)
        lay.addLayout(row)
        row2 = QHBoxLayout()
        self.info = QLabel("")
        self.info.setObjectName("hint")
        row2.addWidget(self.info, 1)
        self.delbtn = QPushButton(T("🗑 حذف المحدد إلى سلة المحذوفات"))
        self.delbtn.clicked.connect(self.delete)
        self.delbtn.setEnabled(False)
        row2.addWidget(self.delbtn)
        lay.addLayout(row2)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.inner = QWidget()
        self.vl = QVBoxLayout(self.inner)
        self.vl.setSpacing(10)
        self.vl.addStretch(1)
        self.scroll.setWidget(self.inner)
        lay.addWidget(self.scroll, 1)
        self.more = QPushButton(T("عرض المزيد"))
        self.more.clicked.connect(self.show_more)
        self.more.hide()
        lay.addWidget(self.more)

    def run(self):
        if self.win.db.count() == 0:
            self.info.setText(T("لازم تفهرس الصور أول (صفحة الفهرسة)."))
            return
        self.info.setText(T("جاري البحث عن المكرر…"))
        QApplication.processEvents()
        self.groups = find_duplicates(self.win.db, self.mode.currentData(), self.win.s.get("dup_threshold", 5))
        for w in self.widgets:
            w.setParent(None)
            w.deleteLater()
        self.widgets = []
        self.shown = 0
        n = sum(len(g["items"]) - 1 for g in self.groups)
        waste = sum(g["waste"] for g in self.groups)
        self.info.setText(T("{g} مجموعة • {n} نسخة زايدة • تكدر توفر {w}").format(g=len(self.groups), n=n, w=human_size(waste))
                          if self.groups else T("ماكو صور مكررة 👌"))
        self.delbtn.setEnabled(bool(self.groups))
        self.show_more()

    def show_more(self):
        for g in self.groups[self.shown:self.shown + self.PAGE]:
            self.shown += 1
            w = DupGroup(self, g, self.shown)
            self.vl.insertWidget(self.vl.count() - 1, w)
            self.widgets.append(w)
        self.more.setVisible(self.shown < len(self.groups))

    def delete(self):
        paths = [p for w in self.widgets for p in w.marked()]
        if not paths:
            return
        if QMessageBox.question(self, APP_NAME, T("تنقل {n} صورة مكررة لسلة المحذوفات؟\n(تكدر ترجعها من السلة إذا احتجتها)").format(n=len(paths))) != QMessageBox.Yes:
            return
        ok = to_trash(paths)
        self.win.db.remove_paths(ok)
        QMessageBox.information(self, APP_NAME, T("انحذفت {n} صورة.").format(n=len(ok)))
        self.run()


# ---------------------------------------------------------------------- indexing
class IndexPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.win = win
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 12)
        lay.setSpacing(12)
        t = QLabel(T("الفهرسة"))
        t.setObjectName("title")
        lay.addWidget(t)
        h = QLabel(T("البرنامج يمر على الأماكن المحددة ويحفظ بصمة لكل صورة. أول مرة تاخذ وقت، ") +
                   T("وبعدها يحدّث بس الصور الجديدة والمعدلة."))
        h.setObjectName("hint")
        h.setWordWrap(True)
        lay.addWidget(h)

        c = card()
        cl = QVBoxLayout(c)
        cl.addWidget(QLabel(T("<b>أماكن البحث</b>")))
        self.list = QListWidget()
        self.list.setMinimumHeight(170)
        cl.addWidget(self.list)
        br = QHBoxLayout()
        add = QPushButton(T("+ إضافة مجلد"))
        add.clicked.connect(self.add_folder)
        rem = QPushButton(T("حذف المحدد"))
        rem.clicked.connect(self.remove_folder)
        br.addWidget(add)
        br.addWidget(rem)
        br.addStretch(1)
        cl.addLayout(br)
        lay.addWidget(c)

        c2 = card()
        g = QVBoxLayout(c2)
        btns = QHBoxLayout()
        self.start = QPushButton(T("▶ ابدأ الفهرسة"))
        self.start.setObjectName("primary")
        self.start.clicked.connect(self.run)
        self.pause = QPushButton(T("⏸ إيقاف مؤقت"))
        self.pause.clicked.connect(self.toggle_pause)
        self.stopb = QPushButton(T("⏹ إيقاف"))
        self.stopb.clicked.connect(lambda: self.win.indexer and self.win.indexer.stop())
        self.rebuild = QPushButton(T("إعادة بناء الفهرس من الصفر"))
        self.rebuild.clicked.connect(self.do_rebuild)
        for b in (self.start, self.pause, self.stopb):
            btns.addWidget(b)
        btns.addStretch(1)
        btns.addWidget(self.rebuild)
        g.addLayout(btns)
        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        g.addWidget(self.bar)
        self.status = QLabel("")
        self.status.setWordWrap(True)
        g.addWidget(self.status)
        self.cur = QLabel("")
        self.cur.setObjectName("hint")
        self.cur.setTextInteractionFlags(Qt.TextSelectableByMouse)
        g.addWidget(self.cur)
        lay.addWidget(c2)
        self.stats = QLabel("")
        self.stats.setObjectName("hint")
        lay.addWidget(self.stats)
        lay.addStretch(1)
        self.fill()
        self.set_running(False)
        self.refresh_stats()

    def fill(self):
        self.list.clear()
        roots = self.win.s.get("roots") or []
        for d in list_drives():
            it = QListWidgetItem("💽  " + T("القرص") + f" {d}")
            it.setData(Qt.UserRole, d)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if (not roots or d in roots) else Qt.Unchecked)
            self.list.addItem(it)
        for r in roots:
            if r not in list_drives():
                it = QListWidgetItem(f"📁  {r}")
                it.setData(Qt.UserRole, r)
                it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
                it.setCheckState(Qt.Checked)
                self.list.addItem(it)

    def roots(self):
        out = []
        for i in range(self.list.count()):
            it = self.list.item(i)
            if it.checkState() == Qt.Checked:
                out.append(it.data(Qt.UserRole))
        return out

    def add_folder(self):
        d = QFileDialog.getExistingDirectory(self, T("اختار مجلد"))
        if d:
            d = os.path.normpath(d)
            it = QListWidgetItem(f"📁  {d}")
            it.setData(Qt.UserRole, d)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked)
            self.list.addItem(it)
            self.save_roots()

    def remove_folder(self):
        for it in self.list.selectedItems():
            if it.data(Qt.UserRole) not in list_drives():
                self.list.takeItem(self.list.row(it))
        self.save_roots()

    def save_roots(self):
        self.win.s["roots"] = self.roots()
        self.win.s.save()

    def run(self):
        if self.win.engine is None:
            self.status.setText(T("الذكاء الاصطناعي بعده يتحمّل… جرب بعد لحظات."))
            return
        roots = self.roots()
        if not roots:
            self.status.setText(T("حدد مكان واحد على الأقل."))
            return
        self.save_roots()
        self.win.start_index(roots)

    def toggle_pause(self):
        if self.win.indexer and self.win.indexer.running:
            p = self.win.indexer.toggle_pause()
            self.pause.setText(T("▶ استئناف") if p else T("⏸ إيقاف مؤقت"))

    def do_rebuild(self):
        if self.win.indexer and self.win.indexer.running:
            return
        if QMessageBox.question(self, APP_NAME, T("تمسح الفهرس الحالي وتبدي من جديد؟")) == QMessageBox.Yes:
            self.win.db.clear()
            self.refresh_stats()
            self.run()

    def set_running(self, on):
        self.start.setEnabled(not on)
        self.rebuild.setEnabled(not on)
        self.pause.setEnabled(on)
        self.stopb.setEnabled(on)
        if not on:
            self.pause.setText(T("⏸ إيقاف مؤقت"))

    def refresh_stats(self):
        self.stats.setText(T("بالفهرس: {n} صورة • {s} • المعالج: {d}").format(n=f"{self.win.db.count():,}", s=human_size(self.win.db.total_size()), d=self.win.engine.device if self.win.engine else '…'))

    def progress(self, st):
        ph = st.get("phase")
        if ph == "scan":
            self.bar.setRange(0, 0)
            self.status.setText(T("🔍 جاري البحث عن الصور… لكيت {f} صورة ({t} جديدة/معدلة) • {d} مجلد").format(f=f"{st['found']:,}", t=f"{st['todo']:,}", d=f"{st['scanned_dirs']:,}"))
        elif ph == "index":
            self.bar.setRange(0, max(1, st["todo"]))
            self.bar.setValue(st["done"])
            rate = st.get("rate", 0)
            left = (st["todo"] - st["done"]) / rate if rate > 0 else 0
            eta = T(" • باقي تقريباً {m} د {s} ث").format(m=int(left//60), s=int(left%60)) if rate > 0 else ""
            self.status.setText(T("🧠 فهرسة {d} / {t} • {r} صورة/ث{eta} • صغيرة متروكة {s} • تالفة {e}").format(d=f"{st['done']:,}", t=f"{st['todo']:,}", r=f"{rate:.0f}", eta=eta, s=f"{st['skipped']:,}", e=f"{st['errors']:,}"))
        elif ph in ("done", "stopped"):
            self.bar.setRange(0, 100)
            self.bar.setValue(100 if ph == "done" else self.bar.value())
            self.status.setText((T("✅ خلصت الفهرسة") if ph == "done" else T("⏹ توقفت الفهرسة")) +
                                T(" • جديد {n} • محذوف من الحاسبة {r}").format(n=f"{st['done'] - st['skipped'] - st['errors']:,}", r=f"{st['removed']:,}"))
            self.set_running(False)
        self.cur.setText(st.get("current", "") if ph not in ("done", "stopped") else "")
        self.refresh_stats()


# ---------------------------------------------------------------------- settings / about
class SettingsPage(QWidget):
    def __init__(self, win):
        super().__init__()
        self.win = win
        s = win.s
        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 20, 22, 12)
        lay.setSpacing(12)
        t = QLabel(T("الإعدادات"))
        t.setObjectName("title")
        lay.addWidget(t)
        c = card()
        g = QGridLayout(c)
        g.setHorizontalSpacing(16)
        g.setVerticalSpacing(12)
        self.gpu = QCheckBox(T("استخدم كارت الشاشة (أسرع) — يتطبق بعد إعادة التشغيل"))
        self.gpu.setChecked(s["use_gpu"])
        g.addWidget(self.gpu, 0, 0, 1, 2)
        self.auto = QCheckBox(T("حدّث الفهرس تلقائياً عند فتح البرنامج"))
        self.auto.setChecked(s["auto_update_index"])
        g.addWidget(self.auto, 1, 0, 1, 2)
        self.upd = QCheckBox(T("بلغني إذا نزل إصدار جديد من البرنامج"))
        self.upd.setChecked(s["check_updates"])
        g.addWidget(self.upd, 2, 0, 1, 2)
        g.addWidget(QLabel(T("تجاهل الصور الأصغر من (KB):")), 3, 0)
        self.minkb = QSpinBox()
        self.minkb.setRange(0, 5000)
        self.minkb.setValue(s["min_kb"])
        g.addWidget(self.minkb, 3, 1)
        g.addWidget(QLabel(T("تجاهل الصور اللي أصغر ضلع بيها أقل من (بكسل) — الأيقونات:")), 4, 0)
        self.minside = QSpinBox()
        self.minside.setRange(0, 2000)
        self.minside.setValue(s["min_side"])
        g.addWidget(self.minside, 4, 1)
        g.addWidget(QLabel(T("دقة كشف المتشابهة (أقل = أدق، أكثر = يلكي تعديلات أكبر):")), 5, 0)
        self.thr = QSpinBox()
        self.thr.setRange(0, 12)
        self.thr.setValue(s["dup_threshold"])
        g.addWidget(self.thr, 5, 1)
        g.addWidget(QLabel(T("لغة البرنامج:")), 6, 0)
        self.lang = QComboBox()
        self.lang.addItem("العربية", "ar")
        self.lang.addItem("English", "en")
        self.lang.setCurrentIndex(0 if lang() == "ar" else 1)
        self.lang.currentIndexChanged.connect(lambda _: win.change_lang(self.lang.currentData()))
        g.addWidget(self.lang, 6, 1)
        lay.addWidget(c)
        sv = QPushButton(T("حفظ"))
        sv.setObjectName("primary")
        sv.clicked.connect(self.save)
        r = QHBoxLayout()
        r.addWidget(sv)
        r.addStretch(1)
        lay.addLayout(r)

        a = card()
        al = QVBoxLayout(a)
        logo = QLabel()
        logo.setPixmap(QPixmap(asset("icon.png")).scaled(88, 88, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top = QHBoxLayout()
        top.addWidget(logo)
        nm = QLabel(f"<div style='font-size:22px;font-weight:800'>{APP_NAME}</div>"
                    "<div style='color:#a9a9b5'>" + T("الإصدار {v} — البحث الذكي عن الصور").format(v=VERSION) + "</div>"
                    f"<div style='margin-top:6px'>{T(CREDIT)}</div>")
        top.addWidget(nm, 1)
        al.addLayout(top)
        links = QHBoxLayout()
        for txt, url in ((T("تليكرام t.me/ibraprogram"), TELEGRAM), (T("تيك توك @ibraprogram"), TIKTOK)):
            b = QPushButton(txt)
            b.clicked.connect(lambda _=False, u=url: QDesktopServices.openUrl(QUrl(u)))
            links.addWidget(b)
        cu = QPushButton(T("فحص التحديثات"))
        cu.clicked.connect(lambda: win.check_updates(manual=True))
        links.addWidget(cu)
        links.addStretch(1)
        al.addLayout(links)
        lay.addWidget(a)
        lay.addStretch(1)

    def save(self):
        s = self.win.s
        s["use_gpu"] = self.gpu.isChecked()
        s["auto_update_index"] = self.auto.isChecked()
        s["check_updates"] = self.upd.isChecked()
        s["min_kb"] = self.minkb.value()
        s["min_side"] = self.minside.value()
        s["dup_threshold"] = self.thr.value()
        s.save()
        QMessageBox.information(self, APP_NAME, T("انحفظت الإعدادات."))


# ====================================================================== main window
class Bridge(QObject):
    progress = Signal(dict)
    engine_ready = Signal(object, str)
    update_found = Signal(object)
    update_none = Signal(str)
    dl_progress = Signal(int)
    dl_done = Signal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.s = Settings()
        self.db = DB()
        self.engine = None
        self.indexer = None
        self.thumbs = Thumbs(200)
        self.br = Bridge()
        self.br.progress.connect(self._progress)
        self.br.engine_ready.connect(self._engine_ready)
        self.br.update_found.connect(self._update_found)
        self.br.update_none.connect(lambda m: QMessageBox.information(self, APP_NAME, m))
        self.br.dl_progress.connect(lambda v: self.upd_btn.setText(T("جاري التنزيل {v}%").format(v=v)))
        self.br.dl_done.connect(self._dl_done)

        self.setWindowTitle(f"{APP_NAME} — " + T("البحث الذكي عن الصور"))
        self.setWindowIcon(QIcon(asset("icon.ico")))
        self.resize(1280, 820)
        self.setLayoutDirection(DIR())

        root = QWidget()
        root.setObjectName("root")
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        side = QFrame()
        side.setObjectName("side")
        side.setFixedWidth(230)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(14, 18, 14, 14)
        sl.setSpacing(6)
        lg = QLabel()
        lg.setPixmap(QPixmap(asset("icon.png")).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        lg.setAlignment(Qt.AlignCenter)
        sl.addWidget(lg)
        b = QLabel(APP_NAME)
        b.setObjectName("brand")
        b.setAlignment(Qt.AlignCenter)
        sl.addWidget(b)
        sb = QLabel(T("البحث الذكي عن الصور"))
        sb.setObjectName("sub")
        sb.setAlignment(Qt.AlignCenter)
        sl.addWidget(sb)
        sl.addSpacing(16)

        self.pages = QStackedWidget()
        self.search = SearchPage(self)
        self.dups = DupPage(self)
        self.index = IndexPage(self)
        self.settings = SettingsPage(self)
        grp = QButtonGroup(self)
        for i, (txt, page) in enumerate(((T("🔎  البحث"), self.search), (T("🧬  الصور المكررة"), self.dups),
                                         (T("📂  الفهرسة"), self.index), (T("⚙  الإعدادات وحول"), self.settings))):
            self.pages.addWidget(page)
            nb = QPushButton(txt)
            nb.setObjectName("nav")
            nb.setCheckable(True)
            nb.setChecked(i == 0)
            nb.clicked.connect(lambda _=False, k=i: self.pages.setCurrentIndex(k))
            grp.addButton(nb)
            sl.addWidget(nb)
        sl.addStretch(1)
        lb = QPushButton("🌐  English" if is_rtl() else "🌐  العربية")
        lb.setToolTip("تغيير اللغة / Change language")
        lb.clicked.connect(lambda: self.change_lang("en" if is_rtl() else "ar"))
        sl.addWidget(lb)
        self.upd_btn = QPushButton("")
        self.upd_btn.setObjectName("primary")
        self.upd_btn.hide()
        self.upd_btn.clicked.connect(self._do_update)
        sl.addWidget(self.upd_btn)
        cr = QLabel(f"{T(CREDIT)}<br><a style='color:#ff6b75' href='{TELEGRAM}'>t.me/ibraprogram</a>")
        cr.setObjectName("sub")
        cr.setAlignment(Qt.AlignCenter)
        cr.setWordWrap(True)
        cr.setOpenExternalLinks(True)
        sl.addWidget(cr)

        h.addWidget(side)
        h.addWidget(self.pages, 1)
        self.setCentralWidget(root)
        self.statusBar().showMessage(T("جاري تحميل الذكاء الاصطناعي…"))
        self._update = None
        self.pending_query = None
        threading.Thread(target=self._load_engine, daemon=True).start()
        if self.s.get("check_updates", True):
            QTimer.singleShot(4000, self.check_updates)

    def showEvent(self, e):
        super().showEvent(e)
        if sys.platform == "win32":
            try:  # شريط عنوان داكن بالوندوز 10/11
                import ctypes
                hwnd = int(self.winId())
                v = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(v), 4)
            except Exception:
                pass

    # -------------------------------------------------- engine
    def _load_engine(self):
        if not models_present():
            self.br.engine_ready.emit(None, T("ملفات الذكاء الاصطناعي ناقصة — أعد تنصيب البرنامج."))
            return
        try:
            eng = create_engine(self.s.get("use_gpu", True))
            self.br.engine_ready.emit(eng, "")
        except Exception as ex:
            self.br.engine_ready.emit(None, T("تعذر تشغيل الذكاء الاصطناعي:") + f" {ex}")

    def _engine_ready(self, eng, err):
        if eng is None:
            self.statusBar().showMessage(err)
            QMessageBox.critical(self, APP_NAME, err)
            return
        self.engine = eng
        n = self.db.count()
        self.statusBar().showMessage(T("جاهز • {d} • بالفهرس {n} صورة").format(d=eng.device, n=f"{n:,}"))
        self.index.refresh_stats()
        if self.pending_query and n:
            self.search.search_image(self.pending_query)
            self.pending_query = None
        if n == 0:
            self.pages.setCurrentIndex(0)
            self.search.ready()
        elif self.s.get("auto_update_index", True):
            roots = self.s.get("roots") or list_drives()
            self.start_index(roots, quiet=True)

    # -------------------------------------------------- indexing
    def start_index(self, roots, quiet=False):
        if self.indexer and self.indexer.running:
            return
        self.indexer = Indexer(self.db, self.engine, self.s, on_progress=self.br.progress.emit)
        self.index.set_running(True)
        self.indexer.start(roots)
        if not quiet:
            self.statusBar().showMessage(T("بدأت الفهرسة…"))

    def _progress(self, st):
        self.index.progress(st)
        ph = st.get("phase")
        if ph == "index":
            self.statusBar().showMessage(T("تحديث الفهرس:") + f" {st['done']:,} / {st['todo']:,}")
        elif ph == "scan":
            self.statusBar().showMessage(T("فحص الملفات… {n} صورة").format(n=f"{st['found']:,}"))
        elif ph in ("done", "stopped"):
            self.statusBar().showMessage(T("جاهز • {d} • بالفهرس {n} صورة").format(d=self.engine.device, n=f"{self.db.count():,}"))
            if self.search.stack.currentIndex() == 0 and self.db.count():
                self.search.show_empty()

    # -------------------------------------------------- updates
    def check_updates(self, manual=False):
        def work():
            try:
                r = updater.check()
                if r:
                    self.br.update_found.emit(r)
                elif manual:
                    self.br.update_none.emit(T("عندك آخر إصدار 👍"))
            except Exception:
                if manual:
                    self.br.update_none.emit(T("ما كدرت أتصل بالإنترنت لفحص التحديثات."))
        threading.Thread(target=work, daemon=True).start()

    def _update_found(self, r):
        self._update = r
        self.upd_btn.setText(T("⬆ تحديث إلى") + f" {r[0]}")
        self.upd_btn.show()

    def _do_update(self):
        if not self._update:
            return
        tag, url, size, notes = self._update
        if QMessageBox.question(self, APP_NAME, T("نزل إصدار جديد") + f" {tag}\n\n{notes[:600]}\n\n" + T("تنزله وتنصبه هسه؟")) != QMessageBox.Yes:
            return
        self.upd_btn.setEnabled(False)

        def work():
            try:
                p = updater.download(url, size, self.br.dl_progress.emit)
                self.br.dl_done.emit(p)
            except Exception:
                self.br.dl_done.emit("")
        threading.Thread(target=work, daemon=True).start()

    def _dl_done(self, path):
        if not path:
            self.upd_btn.setEnabled(True)
            self.upd_btn.setText(T("⬆ إعادة محاولة التحديث"))
            return
        if self.indexer:
            self.indexer.stop()
        updater.install(path)

    def change_lang(self, lg):
        if lg == lang():
            return
        self.s["lang"] = lg
        self.s.save()
        set_lang(lg)  # الرسالة باللغة الجديدة
        r = QMessageBox.question(self, APP_NAME, T("تتغير اللغة بعد إعادة تشغيل البرنامج. تعيد التشغيل هسه؟"))
        if r == QMessageBox.Yes:
            if self.indexer:
                self.indexer.stop()
            restart_app()

    def closeEvent(self, e):
        if self.indexer:
            self.indexer.stop()
        super().closeEvent(e)


def run():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ibrata2.ibralens")
        except Exception:
            pass
    set_lang(Settings().get("lang", "ar"))
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setLayoutDirection(DIR())
    app.setStyleSheet(QSS.replace("%ALIGN%", "right" if is_rtl() else "left"))
    app.setWindowIcon(QIcon(asset("icon.ico")))
    w = MainWindow()
    w.show()
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        w.pending_query = sys.argv[1]
    sys.exit(app.exec())

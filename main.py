import sys, random, time, os, json
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QFrame, QStackedWidget, QGraphicsOpacityEffect,
    QScrollArea, QGridLayout
)
from PyQt6.QtCore import (
    Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve,
    QRect, QPoint, QSequentialAnimationGroup, QPauseAnimation,
    QParallelAnimationGroup, pyqtProperty, QObject
)
from PyQt6.QtGui import (
    QFont, QFontDatabase, QColor, QPainter, QPen, QBrush,
    QLinearGradient, QPainterPath, QRadialGradient,
    QPixmap  # ← این خط اضافه شد
)
import re

def normalize(text):
    text = text.strip()
    # خط 20: حذف شود (نیم‌فاصله نباید تبدیل به فاصله شود)
    # text = text.replace('\u200c', ' ')   ← حذف
    text = text.replace('\u00A0', ' ')
    text = re.sub(r' +', ' ', text)        # خط 22: \s+ → ' +' (فقط فاصله معمولی فشرده شود)
    return text



BASE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(BASE, "fonts")
SAVE_FILE = os.path.join(BASE, "progress.json")

def load_fonts():
    ids = {}
    for name, weight in [
        ("Vazirmatn-Regular", "Regular"),
        ("Vazirmatn-Medium",  "Medium"),
        ("Vazirmatn-Bold",    "Bold"),
        ("Vazirmatn-Black",   "Black"),
    ]:
        path = os.path.join(FONTS_DIR, f"{name}.ttf")
        if os.path.exists(path):
            fid = QFontDatabase.addApplicationFont(path)
            if fid != -1:
                ids[weight] = fid
    return ids

# ── Colors ─────────────────────────────────────────────────────────────────
BG       = "#0A0A0A"
SURFACE  = "#111111"
CARD     = "#161616"
BORDER   = "#2A1A0A"
ACCENT   = "#FF4500"   # deep orange-red
ACCENT2  = "#FF6B00"   # orange
ACCENT3  = "#FF0000"   # pure red
GLOW     = "#FF6600"
SUCCESS  = "#00FF88"
ERROR    = "#FF2244"
WARNING  = "#FFB300"
TEXT     = "#F5F0EB"
MUTED    = "#7A6A5A"
MUTED2   = "#2A2018"
HIGHLIGHT= "#1E1008"
FIRE1    = "#FF4500"
FIRE2    = "#FF6B00"
FIRE3    = "#FFB300"

VAZIR    = "Vazirmatn"

FA_MAP = {
    'q':'ض','w':'ص','e':'ث','r':'ق','t':'ف','y':'غ','u':'ع','i':'ه','o':'خ','p':'ح',
    'a':'ش','s':'س','d':'ی','f':'ب','g':'ل','h':'ا','j':'ت','k':'ن','l':'م',';':'ک',
    'z':'ظ','x':'ط','c':'ز','v':'ر','b':'ذ','n':'د','m':'پ',',':"و",'.':'.',
    'Q':'ِ','W':'ً','E':'ّ','R':'ُ','T':'ل','Y':'إ','U':'أ','I':'آ','O':'»','P':'«',
    'A':'ؤ','S':'ئ','D':'ي','F':'ٍ','G':'لا','H':'آ','J':'ة','K':'»','L':'«',
}

# ── 100 LESSONS ────────────────────────────────────────────────────────────
def build_lessons():
    lessons = []

    # LEVEL 1-3: اشاره
    # ردیف وسط: ب(F) ل(G) ا(H) ت(J)
    lessons.append({
        "id":1,"title":"درس ۱","subtitle":"اشاره چپ – ب (F)",
        "icon":"☝️","color":FIRE1,
        "desc":"انگشت اشاره چپ روی «ب» (F) بنشین","fingers":"اشاره چپ: ب (F)",
        "words":["باب","بابا","بلا","لبه","بال","لب","بلد","بالا"],
        "hint_keys":['f','g'],"target_wpm":6,"target_acc":85,
    })
    lessons.append({
        "id":2,"title":"درس ۲","subtitle":"اشاره راست – ت (J)",
        "icon":"☝️","color":FIRE1,
        "desc":"انگشت اشاره راست روی «ت» (J)","fingers":"اشاره راست: ت (J)",
        "words":["تالاب","اتاق","تلاش","تاب","تالار","الان","اتاق","تالار"],
        "hint_keys":['j','h'],"target_wpm":6,"target_acc":85,
    })
    lessons.append({
        "id":3,"title":"درس ۳","subtitle":"اشاره – ترکیب ب و ت",
        "icon":"☝️","color":FIRE1,
        "desc":"هر دو اشاره با هم","fingers":"اشاره: ب (F)  |  ت (J)",
        "words":["تابلو","لب تاب","تبلت","ابتلا","تابناک","بالاتر","بلاتکلیف","تالاب"],
        "hint_keys":['f','j','g','h'],"target_wpm":8,"target_acc":85,
    })

    # LEVEL 4-6: میانی
    # ردیف وسط: ی(D)  ن(K)
    lessons.append({
        "id":4,"title":"درس ۴","subtitle":"میانی چپ – ی (D)",
        "icon":"🤞","color":FIRE2,
        "desc":"انگشت میانی چپ روی «ی» (D)","fingers":"میانی چپ: ی (D)",
        "words":["یاب","یتیم","بیات","بیا","بیتا","دیدار","ایده","دیار"],
        "hint_keys":['d','f','g'],"target_wpm":8,"target_acc":85,
    })
    lessons.append({
        "id":5,"title":"درس ۵","subtitle":"میانی راست – ن (K)",
        "icon":"🤞","color":FIRE2,
        "desc":"انگشت میانی راست روی «ن» (K)","fingers":"میانی راست: ن (K)",
        "words":["نان","نبات","تنبل","نیاز","نیت","ناتو","نکته","انتن"],
        "hint_keys":['k','j','h'],"target_wpm":8,"target_acc":85,
    })
    lessons.append({
        "id":6,"title":"درس ۶","subtitle":"میانی – ترکیب ی و ن",
        "icon":"🤞","color":FIRE2,
        "desc":"هر دو میانی با هم","fingers":"میانی: ی (D)  |  ن (K)",
        "words":["بین","نیاز","بنیان","تنیدن","دانش","نیاکان","دنیا","بندر","دیوان","نیاید"],
        "hint_keys":['d','k','f','j'],"target_wpm":10,"target_acc":85,
    })

    # LEVEL 7-9: حلقه
    # ردیف وسط: س(S)  م(L)
    lessons.append({
        "id":7,"title":"درس ۷","subtitle":"حلقه چپ – س (S)",
        "icon":"💍","color":FIRE3,
        "desc":"انگشت حلقه چپ روی «س» (S)","fingers":"حلقه چپ: س (S)",
        "words":["سیب","سبد","سینا","بست","سیل","ستاد","سبک","ستون"],
        "hint_keys":['s','d','f'],"target_wpm":10,"target_acc":85,
    })
    lessons.append({
        "id":8,"title":"درس ۸","subtitle":"حلقه راست – م (L)",
        "icon":"💍","color":FIRE3,
        "desc":"انگشت حلقه راست روی «م» (L)","fingers":"حلقه راست: م (L)",
        "words":["ماست","متن","منت","مینا","تمام","ستم","مناسب","مستند"],
        "hint_keys":['l','k','j'],"target_wpm":10,"target_acc":85,
    })
    lessons.append({
        "id":9,"title":"درس ۹","subtitle":"حلقه – ترکیب س و م",
        "icon":"💍","color":FIRE3,
        "desc":"هر دو حلقه با هم","fingers":"حلقه: س (S)  |  م (L)",
        "words":["سیما","مستی","سمند","سیمان","مستقیم","دسترس","سیستم","مستانه","ستمگر","سمندر"],
        "hint_keys":['s','l','d','k'],"target_wpm":12,"target_acc":85,
    })

    # LEVEL 10: کوچک
    # ردیف وسط: ش(A)  ک(;)
    lessons.append({
        "id":10,"title":"درس ۱۰","subtitle":"کوچک – ش و ک",
        "icon":"🤙","color":WARNING,
        "desc":"کوچک چپ: ش (A)  |  کوچک راست: ک (;)","fingers":"کوچک چپ: ش (A)  |  کوچک راست: ک (;)",
        "words":["شک","کاش","شکم","اشک","کشتی","دانشکده","کشمکش","آشکار","شکست","کوشش"],
        "hint_keys":['a',';','s','l'],"target_wpm":12,"target_acc":85,
    })

    # LEVEL 11-20: ردیف بالا + ترکیب
    # ردیف بالا: ض(Q) ص(W) ث(E) ق(R) ف(T) غ(Y) ع(U) ه(I) خ(O) ح(P)
    upper_row_words = [
        # درس ۱۱: ق و ف
        ["قفل","فقه","قفس","قوف","فقط","قفسه","فقیه","قفل‌ساز"],
        # درس ۱۲: غ و ع
        ["غصه","عقل","غرق","عفو","غیب","عقب","غذا","عقده"],
        # درس ۱۳: خ و ح
        ["خوب","حال","خط","حق","خاک","حرف","خون","حساب"],
        # درس ۱۴: ث و ص
        ["صبر","ثبت","صبح","ثروت","صخره","ثقیل","صفحه","ثمر"],
        # درس ۱۵: ض و ه
        ["ضعف","هدف","ضرر","هنر","ضربه","هوش","ضخیم","هراس"],
        # درس ۱۶: ترکیب ۱
        ["قصه","خصم","حقه","فضا","غصب","ضعف","صخره","عفو"],
        # درس ۱۷: ترکیب ۲
        ["خصوصی","قضاوت","حقوقی","فضاحت","غیرعلنی","ضعیف","صخره‌ای","عقوبت"],
        # درس ۱۸: کلمات پرکاربرد
        ["خوبی","حقیقت","قضیه","فرهنگ","غریبه","صبوری","ضروری","هویت"],
        # درس ۱۹: ترکیب پیشرفته
        ["خصوصیت","حقوق‌بشر","قضاوت‌گر","فضاپیما","غیرعادی","صفحه‌کلید","ضخامت","هوشمند"],
        # درس ۲۰: تسلط کامل
        ["خلاصه کردن","حق داشتن","قضاوت نکن","فرق دارد","غذا خوردن","صبور باش","ضرورت دارد","هوشیار باش"],
    ]
    upper_subtitles = [
        "ردیف بالا – ق و ف","ردیف بالا – غ و ع","ردیف بالا – خ و ح",
        "ردیف بالا – ث و ص","ردیف بالا – ض","ردیف بالا – ترکیب ۱",
        "ردیف بالا – ترکیب ۲","ردیف بالا – تکرار","ردیف بالا – ترکیب پیشرفته","ردیف بالا – تسلط کامل"
    ]
    for i in range(10):
        lessons.append({
            "id":11+i,"title":f"درس {11+i}","subtitle":upper_subtitles[i],
            "icon":"⬆️","color":FIRE1,
            "desc":f"تمرین ردیف بالا – {upper_subtitles[i]}","fingers":"ردیف بالا فعال",
            "words":upper_row_words[i],
            "hint_keys":list("qwertyuiop"),"target_wpm":12+i,"target_acc":85,
        })

    # LEVEL 21-30: ردیف پایین
    lower_row_words = [
        # درس ۲۱: ز و ر
        ["زار","راز","روز","زود","ریز","زیر","رزم","زور"],
        # درس ۲۲: ذ و د
        ["دور","داد","ذره","درد","دود","ذکر","دارو","ذهن"],
        # درس ۲۳: پ و و
        ["پود","پور","وارد","پاک","ورود","پیاز","وزن","پیروز"],
        # درس ۲۴: ط و ظ
        ["طرز","ظرف","طراز","ظریف","طراوت","ظاهر","طولانی","ظرفیت"],
        # درس ۲۵: ترکیب ۱
        ["زرد","روزانه","دارو","پرواز","ذرات","وارد","طرز","ظریف"],
        # درس ۲۶: تکرار
        ["زودرس","دیروز","پردازش","روزمره","ذخیره","وزارت","طراحی","ظرافت"],
        # درس ۲۷: با وسط
        ["درست","دوست","پوست","روزی","زندگی","دستور","پرونده","روشنی"],
        # درس ۲۸: ترکیب پیشرفته
        ["پرواز کردن","زود رفتن","دور زدن","ریزه‌کاری","طرز پخت","ظرف دارو","روز پر","وارد شدن"],
        # درس ۲۹: تسلط ۱
        ["زردآلو","پودر کردن","دروازه‌بان","روزنامه","ذره‌بین","وزیر دارد","زردچوبه","پرداختن"],
        # درس ۳۰: تسلط ۲
        ["پیاز داغ","زود بیا","دور برگرد","ریز ریز","طراح داریم","ظرف بزرگ","روز خوب","وارد کار"],
    ]
    lower_subtitles = [
        "ردیف پایین – ز و ر","ردیف پایین – ذ و د","ردیف پایین – پ و و",
        "ردیف پایین – ط و ظ","ردیف پایین – ترکیب ۱","ردیف پایین – تکرار",
        "ردیف پایین – با وسط","ردیف پایین – ترکیب پیشرفته","ردیف پایین – تسلط ۱","ردیف پایین – تسلط ۲"
    ]
    for i in range(10):
        lessons.append({
            "id":21+i,"title":f"درس {21+i}","subtitle":lower_subtitles[i],
            "icon":"⬇️","color":FIRE2,
            "desc":f"تمرین ردیف پایین – {lower_subtitles[i]}","fingers":"ردیف پایین فعال",
            "words":lower_row_words[i],
            "hint_keys":list("zxcvbnm,."),"target_wpm":14+i,"target_acc":85,
        })

    # LEVEL 31-40: کلمات فارسی پرکاربرد
    word_groups = [
        ["من","تو","ما","این","آن","در","از","به","که","با"],
        ["یک","هم","نه","بله","اما","پس","اگر","چون","تا","هر"],
        ["نیست","هست","شد","کرد","بود","می","را","رفت","آمد","دید"],
        ["خوب","بد","بزرگ","کوچک","تازه","قدیم","زیاد","کم","تند","کند"],
        ["خانه","مدرسه","کار","کتاب","درس","دوست","شهر","راه","روز","شب"],
        ["می‌رود","می‌آید","می‌خورد","می‌گوید","می‌داند","می‌خواهد","می‌شود","می‌کند","می‌بیند","می‌نشیند"],
        ["ایران","تهران","اصفهان","شیراز","مشهد","تبریز","اهواز","کرمان","رشت","قم"],
        ["مادر","پدر","خواهر","برادر","پسر","دختر","عمو","خاله","دایی","عمه"],
        ["خوردن","رفتن","آمدن","دیدن","گفتن","شنیدن","نوشتن","خواندن","خوابیدن","بازی"],
        ["امروز","فردا","دیروز","هفته","ماه","سال","صبح","ظهر","عصر","شب"],
    ]
    word_subtitles = [
        "ضمایر و حروف اضافه","کلمات ربط","افعال پرکاربرد","صفات پرکاربرد",
        "اسامی روزمره","افعال مرکب","شهرهای ایران","اعضای خانواده","مصدرها","زمان و روز"
    ]
    for i in range(10):
        lessons.append({
            "id":31+i,"title":f"درس {31+i}","subtitle":word_subtitles[i],
            "icon":"💬","color":FIRE3,
            "desc":f"کلمات پرکاربرد فارسی – {word_subtitles[i]}","fingers":"همه انگشتان",
            "words":word_groups[i],
            "hint_keys":list("asdfghjkl;qwertyuiopcvbn"),"target_wpm":18+i,"target_acc":85,
        })

    # LEVEL 41-100: جملات واقعی (از ساده به پیشرفته)
    sentences_by_level = [
        # 41-50: جملات خیلی ساده
        [
            ["من خوبم","تو کجایی","او رفت","ما آمدیم","شما چطورید"],
            ["کتاب کجاست","قلم دارم","سلام دوستم","ممنون از تو","خوش آمدی"],
            ["هوا خوبه","امروز سرده","فردا گرمه","باران میاد","آفتاب داره"],
            ["نان بخور","آب بنوش","بنشین اینجا","بلند شو","بیا پیشم"],
            ["دوستت دارم","مراقب خودت باش","حالت خوبه","چی شده","بگو بدونم"],
            ["این چیه","اون کیه","کجا میری","کی میاد","چرا رفتی"],
            ["خانه‌ام اینجاست","کارم خوبه","درسم سخته","دوستم نیست","اینجا قشنگه"],
            ["ممنون خیلی","خواهش می‌کنم","ببخشید من","عذرخواهم من","مشکلی نیست"],
            ["صبح بخیر","شب بخیر","روز بخیر","عصر بخیر","ظهر بخیر"],
            ["راستش اینه","فکر می‌کنم","مطمئنم که","امیدوارم که","می‌دانم که"],
        ],
        # 51-60: جملات ساده
        [
            ["من هر روز صبح زود بیدار می‌شوم","تو چه وقت می‌خوابی","او کتاب می‌خواند","ما با هم غذا می‌خوریم"],
            ["کتاب‌هایم را برایم بیاور","قلم آبی روی میز است","مدرسه‌ام نزدیک خانه است","دوستم دیروز آمد"],
            ["هوای تهران امروز خوب است","باران باعث سرما می‌شود","آفتاب تابستان گرم است","زمستان برف می‌بارد"],
            ["لطفاً در را ببند","پنجره را باز کن","چراغ را روشن کن","تلویزیون را خاموش کن"],
            ["دوستت دارم از ته قلب","خیلی دلم برایت تنگ شده","مراقب خودت باش همیشه","به سلامتی شما"],
            ["فردا امتحان مهمی دارم","درس شب را خواندی","معلم توضیح داد خوب","نمره خوبی گرفتم"],
            ["بازار امروز شلوغ بود","خرید کردم برای خانه","قیمت‌ها گران شده","تخفیف خوبی داد"],
            ["ورزش برای سلامتی مهم است","هر روز پیاده‌روی می‌کنم","باشگاه می‌روم سه بار","بدنم قوی‌تر شده"],
            ["برنامه‌ریزی کار را راحت می‌کند","وقتم را مدیریت می‌کنم","کارها را اولویت‌بندی کن","موفقیت نیاز به تلاش دارد"],
            ["کامپیوترم خراب شده امروز","باید تعمیر کنم سریع","پشتیبان گیری مهم است","داده‌هایم از دست رفت"],
        ],
        # 61-70: جملات متوسط
        [
            ["تمرین مداوم کلید موفقیت در تایپ سریع است","هر روز باید تمرین کنی تا پیشرفت کنی","سرعت تایپ با تکرار افزایش پیدا می‌کند"],
            ["ایران کشوری با تاریخ و تمدن چند هزار ساله است","فرهنگ و هنر ایران در جهان شناخته شده است","مردم ایران مهمان‌نواز و صمیمی هستند"],
            ["برنامه‌نویسی مهارتی است که در دنیای امروز بسیار ارزشمند است","یادگیری کدنویسی درهای جدیدی را باز می‌کند","تکنولوژی دنیا را متحول کرده است"],
            ["کتاب خواندن باعث افزایش دانش و خلاقیت می‌شود","هر کتاب دنیایی نو به تو نشان می‌دهد","کتابخانه گنجینه‌ای از دانش بشری است"],
            ["موسیقی روح را آرام می‌کند و احساسات را بیان می‌کند","هنر بازتاب درون هنرمند است","خلاقیت هدیه‌ای است که باید پرورش داد"],
            ["سفر بهترین راه برای شناخت فرهنگ‌های مختلف است","دیدن جاهای جدید دیدگاه انسان را گسترش می‌دهد","هر شهر داستانی دارد که باید شنید"],
            ["تغذیه سالم پایه سلامتی جسم و روح است","میوه و سبزیجات ویتامین‌های ضروری دارند","آب کافی بنوش تا بدنت سالم بماند"],
            ["دوستی یکی از زیباترین روابط انسانی است","دوست خوب در سختی کنارت می‌ماند","ارزش دوستی واقعی را بدان"],
            ["آموزش و یادگیری مستمر ضامن پیشرفت است","هیچ وقت برای یادگیری دیر نیست","هر روز چیز جدیدی یاد بگیر"],
            ["محیط زیست را باید حفظ کرد برای نسل‌های آینده","آلودگی هوا بزرگترین چالش شهرهای بزرگ است","طبیعت میراث مشترک همه ما است"],
        ],
        # 71-80: جملات پیشرفته‌تر
        [
            ["در دنیای دیجیتال امروز مهارت تایپ سریع یک ضرورت است نه یک لوکس","هر برنامه‌نویس حرفه‌ای باید با سرعت بالا تایپ کند","تسلط به صفحه کلید زمان کار را به شدت کاهش می‌دهد"],
            ["هوش مصنوعی در حال تغییر اساسی تمام صنایع دنیا است","یادگیری ماشین به کامپیوترها قدرت تفکر می‌دهد","آینده متعلق به کسانی است که با تکنولوژی دوست هستند"],
            ["فلسفه یونان باستان پایه تفکر غربی را بنا نهاد","سقراط گفت تنها چیزی که می‌دانم این است که نمی‌دانم","ارسطو استاد همه علوم در زمان خود بود"],
            ["اقتصاد ایران با وجود چالش‌ها ظرفیت بالایی دارد","صنعت نفت و گاز منبع مهم درآمد ملی است","کشاورزی و صنعت باید با هم رشد کنند"],
            ["تحقیقات علمی موتور محرک توسعه جوامع پیشرفته است","دانشگاه‌ها مراکز تولید دانش و نوآوری هستند","سرمایه‌گذاری در آموزش بهترین سرمایه‌گذاری است"],
            ["مدیریت زمان مهم‌ترین مهارت در دنیای پررقابت امروز است","اولویت‌بندی درست تفاوت موفقان و شکست‌خوردگان را می‌سازد","هر دقیقه ارزشمند است اگر درست استفاده شود"],
            ["روانشناسی مثبت بر نقاط قوت به جای ضعف تمرکز می‌کند","ذهنیت رشد باور به توانایی پیشرفت است","خوش‌بینی واقع‌بینانه کلید شادی پایدار است"],
            ["ادبیات فارسی از غنی‌ترین ادبیات جهان به شمار می‌رود","حافظ و سعدی شعرایی هستند که جهانی شدند","مولانا با مثنوی معنوی پلی بین فرهنگ‌ها زد"],
            ["ریاضیات زبان طبیعت و کلید درک کیهان است","فیزیک کوانتوم دنیای زیر اتم را توصیف می‌کند","نسبیت اینشتین مفهوم زمان را دگرگون کرد"],
            ["جنبش‌های اجتماعی نیروی محرک تغییرات تاریخی بوده‌اند","حقوق بشر دستاورد مبارزات چندین نسل است","برابری و عدالت آرمان همیشگی بشریت است"],
        ],
        # 81-90: جملات سخت
        [
            ["برنامه‌نویسی شیءگرا یک پارادایم قدرتمند در توسعه نرم‌افزار است","کپسوله‌سازی وراثت و چندریختی ارکان اصلی OOP هستند","طراحی الگوهای نرم‌افزاری راه‌حل‌های آزموده شده هستند"],
            ["پایگاه داده رابطه‌ای اساس اکثر سیستم‌های اطلاعاتی مدرن است","SQL زبان استاندارد کار با پایگاه داده‌های رابطه‌ای است","نرمال‌سازی داده از تکرار و ناسازگاری جلوگیری می‌کند"],
            ["معماری میکروسرویس برنامه را به سرویس‌های کوچک مستقل تقسیم می‌کند","Docker و Kubernetes ابزارهای استقرار مدرن هستند","DevOps فرهنگ همکاری توسعه و عملیات است"],
            ["امنیت سایبری در عصر دیجیتال یک اولویت حیاتی است","رمزنگاری پایه حفاظت از اطلاعات حساس است","هکرهای کلاه سفید سیستم‌ها را امن‌تر می‌کنند"],
            ["یادگیری عمیق با شبکه‌های عصبی چند لایه کار می‌کند","پردازش زبان طبیعی ارتباط انسان و ماشین را ممکن می‌سازد","بینایی ماشین به کامپیوترها دیدن را یاد می‌دهد"],
            ["بلاک‌چین یک دفتر کل توزیع شده و تغییرناپذیر است","ارزهای دیجیتال سیستم مالی را در حال تغییر هستند","قراردادهای هوشمند اجرای خودکار توافقات را ممکن می‌سازند"],
            ["اینترنت اشیاء دنیای فیزیکی و دیجیتال را متصل می‌کند","سنسورهای هوشمند داده‌های ارزشمندی تولید می‌کنند","شهرهای هوشمند از IoT برای بهبود کیفیت زندگی استفاده می‌کنند"],
            ["رایانش ابری زیرساخت IT را به سرویس تبدیل کرده است","مقیاس‌پذیری الاستیک مزیت اصلی فضای ابری است","امنیت داده در فضای ابری چالش مهمی است"],
            ["تجربه کاربری خوب محصولات دیجیتال را متمایز می‌کند","طراحی رابط کاربری باید ساده و شهودی باشد","تحقیقات کاربری پایه طراحی محصول موفق است"],
            ["متدولوژی اجایل توسعه نرم‌افزار را انعطاف‌پذیر کرده است","اسکرام یک چارچوب مدیریت پروژه چابک است","بهبود مستمر ارزش اصلی فرهنگ اجایل است"],
        ],
        # 91-100: جملات خیلی سخت - پاراگراف‌های کامل
        [
            ["در دنیایی که سرعت تغییرات تکنولوژیک روز به روز افزایش می‌یابد مهارت‌های دیجیتال نه یک مزیت رقابتی بلکه یک ضرورت بقا هستند"],
            ["هوش مصنوعی مولد که توانایی تولید متن تصویر موسیقی و کد را دارد در حال بازتعریف مرزهای خلاقیت انسانی است"],
            ["برنامه‌نویس‌های حرفه‌ای می‌دانند که نوشتن کد خوانا و قابل نگهداری به مراتب مهم‌تر از نوشتن کد پیچیده و غیرقابل فهم است"],
            ["مطالعات نشان می‌دهد که افرادی که با ده انگشت تایپ می‌کنند در مقایسه با افرادی که با دو انگشت تایپ می‌کنند تا سه برابر سریع‌تر هستند"],
            ["سیستم‌های توزیع شده با چالش‌هایی مانند سازگاری در دسترس بودن و تحمل خرابی روبرو هستند که CAP theorem آن را فرموله می‌کند"],
            ["الگوریتم‌های یادگیری ماشین با پیدا کردن الگوها در داده‌های آموزشی مدل‌هایی می‌سازند که می‌توانند داده‌های جدید را دسته‌بندی یا پیش‌بینی کنند"],
            ["امنیت اطلاعات در سازمان‌های مدرن باید رویکردی چندلایه داشته باشد که شامل امنیت فیزیکی شبکه برنامه و داده می‌شود"],
            ["در فلسفه تکنولوژی این سوال مطرح است که آیا ابزارها ارزش‌خنثی هستند یا اینکه ارزش‌ها و ایدئولوژی‌های سازندگانشان را در خود جای می‌دهند"],
            ["پیشرفت علم رایانش از ماشین‌های مکانیکی اولیه تا کامپیوترهای کوانتومی امروزی داستان شگفت‌انگیز مبارزه انسان با محدودیت‌های محاسباتی است"],
            ["تیم code_rah با افتخار این سیستم آموزش تایپ را برای تمام کسانی که می‌خواهند در دنیای دیجیتال تسلط کامل داشته باشند طراحی کرده است"],
        ],
    ]

    # Build levels 41-100
    sentence_idx = 0
    for group_idx, group in enumerate(sentences_by_level):
        for sub_idx, sentence_list in enumerate(group):
            lid = 41 + sentence_idx
            target_wpm = 20 + sentence_idx
            target_acc = 85
            lessons.append({
                "id": lid,
                "title": f"درس {lid}",
                "subtitle": f"جملات واقعی – سطح {group_idx+1}",
                "icon": ["📝","📖","💡","🔥","⚡","🎯","🏆","💻","🌟","👑"][group_idx],
                "color": [FIRE1,FIRE2,FIRE3,WARNING,SUCCESS,ACCENT2,ACCENT,FIRE1,FIRE2,FIRE3][group_idx],
                "desc": f"تایپ جملات واقعی فارسی – سطح {group_idx+1} از ۶",
                "fingers": "همه انگشتان – تمرکز روی دقت و سرعت",
                "words": sentence_list,
                "hint_keys": list("asdfghjkl;qwertyuiopzxcvbnm"),
                "target_wpm": target_wpm,
                "target_acc": target_acc,
            })
            sentence_idx += 1
    for l in lessons:
        l["target_wpm"] = max(3, int(l["target_wpm"] * 0.4))
    return lessons[:100]
    return lessons[:100]

LESSONS = build_lessons()
WORDS_PER_ROUND = 5

# ── Save / Load ────────────────────────────────────────────────────────────
def save_progress(progress):
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except: pass

def load_progress():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
    except: pass
    return {}

# ── Animated glowing background ────────────────────────────────────────────
class GlowBg(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def _tick(self):
        self._phase = (self._phase + 0.012) % (2 * 3.14159)
        self.update()

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(BG))

        for cx, cy, radius, color_hex, phase_offset in [
            (w * 0.1,  h * 0.1,  350, "#FF4500", 0.0),
            (w * 0.9,  h * 0.9,  300, "#FF6B00", 1.05),
            (w * 0.5,  h * 0.5,  200, "#FF0000", 2.1),
            (w * 0.8,  h * 0.2,  250, "#FFB300", 3.0),
        ]:
            pulse = 0.06 + 0.03 * math.sin(self._phase + phase_offset)
            grad = QRadialGradient(cx, cy, radius)
            c = QColor(color_hex)
            c.setAlphaF(pulse)
            grad.setColorAt(0, c)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(int(cx - radius), int(cy - radius), radius * 2, radius * 2)

        pen = QPen(QColor(255, 80, 0, 6))
        pen.setWidth(1)
        p.setPen(pen)
        step = 55
        for x in range(0, w, step):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, step):
            p.drawLine(0, y, w, y)
        p.end()


# ── Monster Coder Brand Widget ──────────────────────────────────────────────
class MonsterBrand(QWidget):
    def __init__(self, size="normal"):
        super().__init__()
        self._phase = 0.0
        self._size = size
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)
        if size == "large":
            self.setFixedHeight(80)
        elif size == "small":
            self.setFixedHeight(34)
        else:
            self.setFixedHeight(50)

    def _tick(self):
        self._phase = (self._phase + 0.04) % (2 * 3.14159)
        self.update()

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(0, 0, 0, 0))

        pulse = 0.7 + 0.3 * math.sin(self._phase)

        if self._size == "large":
            font_size = 28
            sub_size = 11
        elif self._size == "small":
            font_size = 13
            sub_size = 0
        else:
            font_size = 18
            sub_size = 9

        # Glow behind text
        for offset in range(8, 0, -2):
            alpha = int(30 * pulse * (9 - offset) / 8)
            p.setPen(QPen(QColor(255, 80, 0, alpha)))
            p.setFont(QFont("Consolas", font_size + offset, QFont.Weight.Black))
            p.drawText(0, 0, w, h - (sub_size + 4 if sub_size else 0),
                       Qt.AlignmentFlag.AlignCenter, "code_rah")

        # Main gradient text simulation
        grad = QLinearGradient(0, 0, w, 0)
        grad.setColorAt(0.0, QColor("#FF0000"))
        grad.setColorAt(0.3, QColor("#FF4500"))
        grad.setColorAt(0.6, QColor("#FF6B00"))
        grad.setColorAt(1.0, QColor("#FFB300"))
        p.setPen(QPen(QColor(FIRE2)))
        p.setFont(QFont("Consolas", font_size, QFont.Weight.Black))
        p.drawText(0, 0, w, h - (sub_size + 4 if sub_size else 0),
                   Qt.AlignmentFlag.AlignCenter, "code_rah")

        if sub_size:
            p.setFont(QFont(VAZIR, sub_size))
            alpha2 = int(180 + 75 * math.sin(self._phase + 1.0))
            p.setPen(QPen(QColor(255, 150, 50, alpha2)))
            p.drawText(0, h - sub_size - 6, w, sub_size + 6,
                       Qt.AlignmentFlag.AlignCenter, "آموزش تایپ حرفه‌ای فارسی")
        p.end()


# ── Persian keyboard widget ─────────────────────────────────────────────────
class PersianKeyboard(QWidget):
    ROWS = [
        [('ض','Q'),('ص','W'),('ث','E'),('ق','R'),('ف','T'),('غ','Y'),('ع','U'),('ه','I'),('خ','O'),('ح','P')],
        [('ش','A'),('س','S'),('ی','D'),('ب','F'),('ل','G'),('ا','H'),('ت','J'),('ن','K'),('م','L'),('ک',';')],
        [('ظ','Z'),('ط','X'),('ز','C'),('ر','V'),('ذ','B'),('د','N'),('پ','M')],
    ]
    FINGER_COLORS = {
        'A':'#EF4444','Q':'#EF4444','Z':'#EF4444',
        'S':'#F97316','W':'#F97316','X':'#F97316',
        'D':'#EAB308','E':'#EAB308','C':'#EAB308',
        'F':'#FF4500','R':'#FF4500','V':'#FF4500','T':'#FF4500','B':'#FF4500','G':'#FF4500',
        'H':'#FF6B00','Y':'#FF6B00','N':'#FF6B00','U':'#FF6B00','J':'#FF6B00',
        'K':'#EAB308','I':'#EAB308','M':'#EAB308',
        'L':'#F97316','O':'#F97316',
        ';':'#EF4444','P':'#EF4444',
    }

    # Persian char → English key reverse map
    FA_TO_EN = {
        'ض':'Q','ص':'W','ث':'E','ق':'R','ف':'T','غ':'Y','ع':'U','ه':'I','خ':'O','ح':'P',
        'ش':'A','س':'S','ی':'D','ب':'F','ل':'G','ا':'H','ت':'J','ن':'K','م':'L','ک':';',
        'ظ':'Z','ط':'X','ز':'C','ر':'V','ذ':'B','د':'N','پ':'M','و':',',
    }

    def __init__(self):
        super().__init__()
        self.hint_keys = set()       # lesson hint keys (dimly highlighted)
        self.next_key = None         # the NEXT key user must press (brightly highlighted)
        # press animation: key → float 0..1 (1=just pressed, fades to 0)
        self._press_anim = {}        # en_key_upper → float
        self._anim_timer = QTimer(self)
        self._anim_timer.timeout.connect(self._tick_anim)
        self._anim_timer.start(16)   # 60fps
        self.setFixedHeight(150)

    def set_hint_keys(self, keys):
        """Lesson-level hint: which finger keys are relevant (dim glow)."""
        self.hint_keys = {k.upper() for k in keys}
        self.update()

    def set_next_key(self, persian_char):
        """Called on every keystroke: highlight the key for the next char to type."""
        if persian_char is None:
            self.next_key = None
        elif persian_char == ' ':
            self.next_key = 'SPACE'
        else:
            self.next_key = self.FA_TO_EN.get(persian_char, None)
            if self.next_key:
                self.next_key = self.next_key.upper()
        self.update()

    def press_key(self, persian_char):
        """Trigger the press animation for the given char's key."""
        if persian_char == ' ':
            en = 'SPACE'
        else:
            en = self.FA_TO_EN.get(persian_char, None)
        if en:
            self._press_anim[en.upper()] = 1.0

    def _tick_anim(self):
        changed = False
        for k in list(self._press_anim):
            self._press_anim[k] -= 0.07   # fade speed
            if self._press_anim[k] <= 0:
                del self._press_anim[k]
            changed = True
        if changed:
            self.update()

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        kw, kh, gap = 38, 38, 5

        for ri, row in enumerate(self.ROWS):
            total = len(row) * (kw + gap) - gap
            ox = (w - total) / 2 + ri * 22
            y_base = ri * (kh + gap) + 8

            for ci, (fa, en) in enumerate(row):
                x = ox + ci * (kw + gap)
                en_up = en.upper()

                is_next    = (en_up == self.next_key)
                is_hint    = (en_up in self.hint_keys)
                press_val  = self._press_anim.get(en_up, 0.0)  # 0..1
                color      = self.FINGER_COLORS.get(en_up, '#374151')

                # Press animation: key sinks down slightly and shrinks
                press_offset = int(press_val * 4)
                press_shrink = int(press_val * 3)
                x_d  = x + press_shrink // 2
                y_d  = y_base + press_offset
                kw_d = kw - press_shrink
                kh_d = kh - press_shrink - press_offset // 2

                # ── outer glow ──────────────────────────────────────────
                if is_next:
                    # Big pulsing glow for the target key
                    glow_r = kw * 1.1
                    glow = QRadialGradient(x + kw/2, y_base + kh/2, glow_r)
                    gc = QColor(color); gc.setAlpha(110)
                    gc2 = QColor(color); gc2.setAlpha(0)
                    glow.setColorAt(0, gc)
                    glow.setColorAt(1, gc2)
                    p.setBrush(QBrush(glow))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawEllipse(int(x - 14), int(y_base - 14), kw + 28, kh + 28)

                elif press_val > 0:
                    # Flash glow on press
                    glow = QRadialGradient(x + kw/2, y_base + kh/2, kw * 0.9)
                    gc = QColor("#FFFFFF"); gc.setAlpha(int(70 * press_val))
                    glow.setColorAt(0, gc)
                    glow.setColorAt(1, QColor(0,0,0,0))
                    p.setBrush(QBrush(glow))
                    p.setPen(Qt.PenStyle.NoPen)
                    p.drawEllipse(int(x - 8), int(y_base - 8), kw + 16, kh + 16)

                # ── key body ────────────────────────────────────────────
                if is_next:
                    # Bright filled key
                    key_color = QColor(color)
                    p.setBrush(key_color)
                    p.setPen(QPen(QColor("#FFFFFF"), 2))
                elif press_val > 0:
                    # Pressed: flash white-ish
                    mix = QColor(color)
                    mix.setAlpha(200)
                    p.setBrush(mix)
                    p.setPen(QPen(QColor("#FFFFFF"), 1.5))
                elif is_hint:
                    # Hint key: slightly lit, colored border
                    bg = QColor(CARD)
                    p.setBrush(bg)
                    border = QColor(color); border.setAlpha(180)
                    p.setPen(QPen(border, 1.2))
                else:
                    # Dim: almost invisible
                    bg = QColor(CARD); bg.setAlpha(140)
                    p.setBrush(bg)
                    dim_border = QColor(color); dim_border.setAlpha(55)
                    p.setPen(QPen(dim_border, 0.8))

                p.drawRoundedRect(int(x_d), int(y_d), kw_d, kh_d, 7, 7)

                # ── Persian letter ──────────────────────────────────────
                if is_next:
                    p.setPen(QPen(QColor("#FFFFFF")))
                    p.setFont(QFont(VAZIR, 12, QFont.Weight.Black))
                elif press_val > 0:
                    p.setPen(QPen(QColor("#FFFFFF")))
                    p.setFont(QFont(VAZIR, 11, QFont.Weight.Bold))
                elif is_hint:
                    p.setPen(QPen(QColor(MUTED)))
                    p.setFont(QFont(VAZIR, 10))
                else:
                    dim_text = QColor(MUTED2); dim_text.setAlpha(160)
                    p.setPen(QPen(dim_text))
                    p.setFont(QFont(VAZIR, 9))

                p.drawText(int(x_d), int(y_d), kw_d, kh_d - 12,
                           Qt.AlignmentFlag.AlignCenter, fa)

                # ── English key label ───────────────────────────────────
                if is_next:
                    p.setPen(QPen(QColor("#FFFFFF")))
                    p.setFont(QFont("Consolas", 7, QFont.Weight.Bold))
                elif is_hint:
                    p.setPen(QPen(QColor(color)))
                    p.setFont(QFont("Consolas", 6))
                else:
                    dim_en = QColor(color); dim_en.setAlpha(60)
                    p.setPen(QPen(dim_en))
                    p.setFont(QFont("Consolas", 6))

                p.drawText(int(x_d), int(y_d + kh_d - 14), kw_d, 14,
                           Qt.AlignmentFlag.AlignCenter, en)

        p.end()


# ── Animated progress bar ───────────────────────────────────────────────────
class GlowProgressBar(QWidget):
    def __init__(self, color=ACCENT):
        super().__init__()
        self._value = 0
        self._max = 100
        self._color = color
        self._anim_val = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._animate)
        self._timer.start(16)
        self.setFixedHeight(12)

    def setValue(self, v): self._value = v
    def setMaximum(self, m): self._max = m

    def _animate(self):
        target = self._value / max(self._max, 1)
        self._anim_val += (target - self._anim_val) * 0.08
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        fill = int(w * self._anim_val)
        p.setBrush(QColor(BORDER))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, w, h, h//2, h//2)
        if fill > 0:
            grad = QLinearGradient(0, 0, fill, 0)
            grad.setColorAt(0, QColor(FIRE1))
            grad.setColorAt(1, QColor(FIRE3))
            p.setBrush(QBrush(grad))
            p.drawRoundedRect(0, 0, fill, h, h//2, h//2)
            glow = QLinearGradient(0, 0, fill, 0)
            gc = QColor(GLOW); gc.setAlpha(130)
            glow.setColorAt(0, QColor(0,0,0,0))
            glow.setColorAt(0.7, QColor(0,0,0,0))
            glow.setColorAt(1, gc)
            p.setBrush(QBrush(glow))
            p.drawRoundedRect(0, 0, fill, h, h//2, h//2)
        p.end()


# ── Typing widget ───────────────────────────────────────────────────────────
class TypingWidget(QWidget):
    finished = pyqtSignal(float, float)

    def __init__(self):
        super().__init__()
        self.words = []
        self.word_index = 0
        self.typed = ""
        self.errors = 0
        self.total_chars_typed = 0
        self.start_time = None
        self.keyboard_ref = None   # injected by LessonScreen
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(12)
        lay.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        card_lay = QVBoxLayout(card)
        card_lay.setContentsMargins(24, 18, 24, 18)

        self.words_lbl = QLabel()
        self.words_lbl.setFont(QFont(VAZIR, 20))
        self.words_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.words_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.words_lbl.setWordWrap(True)
        self.words_lbl.setStyleSheet(f"color:{MUTED}; letter-spacing:3px; background:transparent;")
        self.words_lbl.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        card_lay.addWidget(self.words_lbl)

        self.input_lbl = QLabel("▮")
        self.input_lbl.setFont(QFont(VAZIR, 20, QFont.Weight.Medium))
        self.input_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_lbl.setMinimumHeight(56)
        self.input_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.input_lbl.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.input_lbl.setWordWrap(True)
        self.input_lbl.setStyleSheet(f"""
            background: {HIGHLIGHT};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 6px 20px;
            letter-spacing: 3px;
            color: {TEXT};
        """)
        card_lay.addWidget(self.input_lbl)
        lay.addWidget(card)

        stats = QHBoxLayout()
        self.wpm_lbl  = self._stat_lbl("⚡ WPM: –")
        self.acc_lbl  = self._stat_lbl("🎯 دقت: –")
        self.prog_lbl = self._stat_lbl("📍 ۱/۵")
        for lb in (self.prog_lbl, self.acc_lbl, self.wpm_lbl):
            stats.addWidget(lb)
        lay.addLayout(stats)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def _stat_lbl(self, text):
        lb = QLabel(text)
        lb.setFont(QFont(VAZIR, 11))
        lb.setStyleSheet(f"color:{MUTED}; background:transparent;")
        lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lb

    def load_words(self, words):
        self.words = words[:]
        self.word_index = 0
        self.typed = ""
        self.errors = 0
        self.total_chars_typed = 0
        self.start_time = None
        self._refresh()
        self._sync_keyboard()

    def _refresh(self):
        parts = []
        for i, w in enumerate(self.words):
            if i < self.word_index:
                parts.append(f'<span style="color:{SUCCESS};">{w}</span>')
            elif i == self.word_index:
                parts.append(f'<span style="color:{TEXT}; font-weight:bold; text-decoration:underline;">{w}</span>')
            else:
                parts.append(f'<span style="color:{MUTED2};">{w}</span>')
        self.words_lbl.setText("   ".join(parts))
        self.prog_lbl.setText(f"📍 {self.word_index+1}/{len(self.words)}")
        self._sync_keyboard()

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text()
        if not self.words: return

        if self.start_time is None and text.strip():
            self.start_time = time.time()

        cur = self.words[self.word_index] if self.word_index < len(self.words) else ""

        # آیا کلمه جاری فاصله دارد؟ (مثل «صفحه کلید»)
        cur_has_space = ' ' in cur

        if key == Qt.Key.Key_Backspace:
            self.typed = self.typed[:-1]
        elif key == Qt.Key.Key_Return and not cur_has_space:
            # اسپس یا اینتر = تأیید کلمه (فقط وقتی کلمه خودش فاصله ندارد)
            self.total_chars_typed += len(cur)
            if self.keyboard_ref:
                self.keyboard_ref.press_key(' ')
            if self.typed == cur:
                self.word_index += 1
                self.typed = ""
                self._refresh()
                if self.word_index >= len(self.words):
                    self._finish(); return
            else:
                err = sum(1 for a, b in zip(self.typed, cur) if a != b) + abs(len(self.typed) - len(cur))
                self.errors += err
                self.typed = ""
        elif key == Qt.Key.Key_Return and cur_has_space:
            # اینتر = تأیید کلمه‌ای که فاصله دارد
            self.total_chars_typed += len(cur)
            if self.keyboard_ref:
                self.keyboard_ref.press_key(' ')
            if self.typed == cur:
                self.word_index += 1
                self.typed = ""
                self._refresh()
                if self.word_index >= len(self.words):
                    self._finish(); return
            else:
                err = sum(1 for a, b in zip(self.typed, cur) if a != b) + abs(len(self.typed) - len(cur))
                self.errors += err
                self.typed = ""
        elif key == Qt.Key.Key_Space:
            cur = self.words[self.word_index] if self.word_index < len(self.words) else ""
            next_pos = len(self.typed)
            if next_pos < len(cur) and cur[next_pos] == ' ':
                if self.keyboard_ref:
                    self.keyboard_ref.press_key(' ')
                self.typed += ' '
            else:
                if self.keyboard_ref:
                    self.keyboard_ref.press_key('\u200c')
                self.typed += '\u200c'

        else:
            raw = text
            if raw.lower() in FA_MAP:
                char = FA_MAP[raw.lower()]
            elif raw in FA_MAP:
                char = FA_MAP[raw]
            else:
                char = raw
            if char and char.isprintable():
                if self.keyboard_ref:
                    self.keyboard_ref.press_key(char)
                self.typed += char

        self._update_input()
        self._update_stats()
        self._sync_keyboard()

    def _sync_keyboard(self):
        """Tell keyboard which key to highlight as 'next to press'."""
        if not self.keyboard_ref:
            return
        if self.word_index >= len(self.words):
            self.keyboard_ref.set_next_key(None)
            return
        cur = self.words[self.word_index]
        next_pos = len(self.typed)
        if next_pos < len(cur):
            self.keyboard_ref.set_next_key(' ' if cur[next_pos] == '\u200c' else cur[next_pos])
        else:
            # word complete, next key is Space
            self.keyboard_ref.set_next_key(' ')

    def _update_input(self):
        cur = self.words[self.word_index] if self.word_index < len(self.words) else ""
        disp = ""
        for i, ch in enumerate(self.typed):
            col = SUCCESS if i < len(cur) and ch == cur[i] else ERROR
            disp += f'<span style="color:{col};">{ch}</span>'
        disp += f'<span style="color:{GLOW};">▮</span>'
        self.input_lbl.setText(disp)

    def _update_stats(self):
        if self.start_time:
            el = time.time() - self.start_time
            chars = sum(len(w) for w in self.words[:self.word_index]) + len(self.typed)
            wpm = (chars / 5) / (el / 60) if el > 0 else 0
            total = max(self.total_chars_typed, 1)
            acc = max(0, 100 - (self.errors / total) * 100)
            self.wpm_lbl.setText(f"⚡ WPM: {int(wpm)}")
            self.acc_lbl.setText(f"🎯 دقت: {int(acc)}%")

    def _finish(self):
        el = time.time() - self.start_time if self.start_time else 1
        chars = sum(len(w) for w in self.words)
        wpm = (chars / 5) / (el / 60) if el > 0 else 0
        total = max(self.total_chars_typed, chars)
        acc = max(0, 100 - (self.errors / max(total, 1)) * 100)
        self.finished.emit(wpm, acc)


# ── Lesson Card (compact for 100 lessons) ─────────────────────────────────
class LessonCard(QWidget):
    clicked = pyqtSignal(int)

    def __init__(self, lesson, unlocked, completed, best_wpm=0):
        super().__init__()
        self.lesson_id = lesson["id"]
        self.unlocked = unlocked
        self._hovered = False
        self.best_wpm = best_wpm
        if unlocked:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(110, 100)
        self._build(lesson, completed)

    def _build(self, l, completed):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 6)
        lay.setSpacing(2)

        top = QHBoxLayout()
        icon = QLabel(l["icon"])
        icon.setFont(QFont("Segoe UI Emoji", 13))
        top.addWidget(icon)
        top.addStretch()
        if completed:
            done = QLabel("✓")
            done.setStyleSheet(f"color:{SUCCESS}; font:bold 14px; background:transparent;")
            top.addWidget(done)
        elif not self.unlocked:
            lock = QLabel("🔒")
            lock.setFont(QFont("Segoe UI Emoji", 10))
            top.addWidget(lock)
        lay.addLayout(top)

        num = QLabel(f"#{l['id']}")
        num.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        num.setStyleSheet(f"color:{l['color']}; background:transparent;")
        lay.addWidget(num)

        title = QLabel(l["title"])
        title.setFont(QFont(VAZIR, 9, QFont.Weight.Bold))
        title.setStyleSheet(f"color:{TEXT if self.unlocked else MUTED}; background:transparent;")
        lay.addWidget(title)

        if self.best_wpm > 0:
            wpm_l = QLabel(f"⚡{self.best_wpm}")
            wpm_l.setFont(QFont("Consolas", 8))
            wpm_l.setStyleSheet(f"color:{WARNING}; background:transparent;")
            lay.addWidget(wpm_l)

    def enterEvent(self, e):
        if self.unlocked: self._hovered = True; self.update()

    def leaveEvent(self, e):
        self._hovered = False; self.update()

    def mousePressEvent(self, e):
        if self.unlocked: self.clicked.emit(self.lesson_id)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        lesson = next(l for l in LESSONS if l["id"] == self.lesson_id)
        color = lesson["color"]

        if self._hovered and self.unlocked:
            glow = QRadialGradient(w/2, h/2, w*0.7)
            gc = QColor(color); gc.setAlpha(50)
            glow.setColorAt(0, gc)
            glow.setColorAt(1, QColor(0,0,0,0))
            p.setBrush(QBrush(glow))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(-8, -8, w+16, h+16, 16, 16)

        bg = QColor(CARD)
        if not self.unlocked: bg.setAlpha(100)
        p.setBrush(bg)
        border_color = QColor(color) if self.unlocked else QColor(BORDER)
        if not self.unlocked: border_color.setAlpha(60)
        p.setPen(QPen(border_color, 1.5 if self._hovered else 1))
        p.drawRoundedRect(0, 0, w, h, 12, 12)

        if self.unlocked:
            grad = QLinearGradient(0, 0, w, 0)
            grad.setColorAt(0, QColor(color))
            grad.setColorAt(1, QColor(FIRE3))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(0, 0, w, 3, 2, 2)

        p.end()
        super().paintEvent(event)


# ── Home Screen ─────────────────────────────────────────────────────────────
class HomeScreen(QWidget):
    lesson_selected = pyqtSignal(int)

    def __init__(self, progress):
        super().__init__()
        self.progress = progress
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border:none; background:transparent; } QScrollBar:vertical { background:#111; width:8px; border-radius:4px; } QScrollBar::handle:vertical { background:#FF4500; border-radius:4px; }")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        content = QWidget()
        content.setStyleSheet("background:transparent;")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(40, 24, 40, 24)
        lay.setSpacing(16)

        # code_rah brand
        brand = MonsterBrand("large")
        lay.addWidget(brand)

        # Tagline
        tagline = QLabel("۱۰۰ مرحله · از صفر تا تسلط کامل · تایپ ۱۰ انگشت فارسی")
        tagline.setFont(QFont(VAZIR, 11))
        tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tagline.setStyleSheet(f"color:{MUTED}; background:transparent; letter-spacing:2px;")
        lay.addWidget(tagline)

        # Divider fire line
        divider = QFrame()
        divider.setFixedHeight(2)
        divider.setStyleSheet(f"background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #FF0000, stop:0.5 #FF6B00, stop:1 #FFB300);")
        lay.addWidget(divider)

        # Overall progress
        done = sum(1 for i in range(1, 101) if self.progress.get(i, {}).get("done"))
        prog_row = QHBoxLayout()
        prog_lbl = QLabel(f"🔥  پیشرفت کلی: {done} از {len(LESSONS)} درس")
        prog_lbl.setFont(QFont(VAZIR, 12))
        prog_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
        prog_row.addWidget(prog_lbl)
        prog_row.addStretch()
        pct = QLabel(f"{int(done/len(LESSONS)*100)}%")
        pct.setFont(QFont("Consolas", 14, QFont.Weight.Black))
        pct.setStyleSheet(f"color:{FIRE2}; background:transparent;")
        prog_row.addWidget(pct)
        lay.addLayout(prog_row)

        pb = GlowProgressBar(ACCENT)
        pb.setMaximum(len(LESSONS))
        pb.setValue(done)
        lay.addWidget(pb)

        # Chapters
        chapters = [
            (1, 3,   "فصل ۱", "انگشت اشاره", "☝️"),
            (4, 6,   "فصل ۲", "انگشت میانی", "🤞"),
            (7, 9,   "فصل ۳", "انگشت حلقه", "💍"),
            (10, 10, "فصل ۴", "انگشت کوچک", "🤙"),
            (11, 20, "فصل ۵", "ردیف بالا", "⬆️"),
            (21, 30, "فصل ۶", "ردیف پایین", "⬇️"),
            (31, 40, "فصل ۷", "کلمات پرکاربرد", "💬"),
            (41, 50, "فصل ۸", "جملات ساده", "📝"),
            (51, 60, "فصل ۹", "جملات متوسط", "📖"),
            (61, 70, "فصل ۱۰", "جملات پیشرفته ۱", "💡"),
            (71, 80, "فصل ۱۱", "جملات پیشرفته ۲", "🔥"),
            (81, 90, "فصل ۱۲", "جملات تخصصی", "💻"),
            (91, 100,"فصل ۱۳", "جملات استاد", "👑"),
        ]

        for start, end, ch_title, ch_sub, ch_icon in chapters:
            ch_done = sum(1 for i in range(start, end+1) if self.progress.get(i,{}).get("done"))
            ch_total = end - start + 1

            ch_hdr = QHBoxLayout()
            ch_lbl = QLabel(f"{ch_icon}  {ch_title} — {ch_sub}")
            ch_lbl.setFont(QFont(VAZIR, 12, QFont.Weight.Bold))
            ch_lbl.setStyleSheet(f"color:{FIRE2}; background:transparent;")
            ch_hdr.addWidget(ch_lbl)
            ch_hdr.addStretch()
            ch_prog = QLabel(f"{ch_done}/{ch_total}")
            ch_prog.setFont(QFont("Consolas", 10))
            ch_prog.setStyleSheet(f"color:{MUTED}; background:transparent;")
            ch_hdr.addWidget(ch_prog)
            lay.addLayout(ch_hdr)

            grid_widget = QWidget()
            grid_widget.setStyleSheet("background:transparent;")
            grid = QHBoxLayout(grid_widget)
            grid.setSpacing(8)
            grid.setAlignment(Qt.AlignmentFlag.AlignLeft)

            for lid in range(start, end+1):
                lesson = next((l for l in LESSONS if l["id"]==lid), None)
                if not lesson: continue
                idx = lid - 1
                unlocked = lid == 1 or self.progress.get(lid-1, {}).get("done", False)
                completed = self.progress.get(lid, {}).get("done", False)
                best_wpm = int(self.progress.get(lid, {}).get("wpm", 0))
                card = LessonCard(lesson, unlocked, completed, best_wpm)
                card.clicked.connect(self.lesson_selected)
                grid.addWidget(card)

            grid.addStretch()
            lay.addWidget(grid_widget)

        # Footer brand
        footer = QLabel("⚡ code_rah © 2025 — All Rights Reserved")
        footer.setFont(QFont("Consolas", 9))
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color:{MUTED}; background:transparent; margin-top:10px;")
        lay.addWidget(footer)

        scroll.setWidget(content)
        outer.addWidget(scroll)


# ── Lesson Screen ────────────────────────────────────────────────────────────
class LessonScreen(QWidget):
    back = pyqtSignal()
    completed = pyqtSignal(int, float, float)

    def __init__(self):
        super().__init__()
        self.lesson = None
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 12, 40, 12)
        lay.setSpacing(10)

        # Top bar
        top = QHBoxLayout()
        back_btn = QPushButton("← برگشت")
        back_btn.setFont(QFont(VAZIR, 11))
        back_btn.setStyleSheet(f"""
            QPushButton {{ background:transparent; color:{MUTED}; border:none; padding:6px 12px; border-radius:8px; }}
            QPushButton:hover {{ background:{HIGHLIGHT}; color:{TEXT}; }}
        """)
        back_btn.clicked.connect(self.back)
        top.addWidget(back_btn)
        top.addStretch()

        brand_small = MonsterBrand("small")
        brand_small.setFixedWidth(200)
        top.addWidget(brand_small)
        top.addStretch()

        self.title_lbl = QLabel()
        self.title_lbl.setFont(QFont(VAZIR, 14, QFont.Weight.Bold))
        self.title_lbl.setStyleSheet(f"color:{FIRE2}; background:transparent;")
        top.addWidget(self.title_lbl)
        lay.addLayout(top)

        # Info card
        info = QFrame()
        info.setStyleSheet(f"QFrame {{ background:{CARD}; border:1px solid {BORDER}; border-radius:14px; }}")
        info_lay = QVBoxLayout(info)
        info_lay.setContentsMargins(16, 10, 16, 10)
        info_lay.setSpacing(4)
        self.desc_lbl = QLabel()
        self.desc_lbl.setFont(QFont(VAZIR, 11))
        self.desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
        self.fingers_lbl = QLabel()
        self.fingers_lbl.setFont(QFont(VAZIR, 12, QFont.Weight.Bold))
        self.fingers_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fingers_lbl.setStyleSheet(f"color:{FIRE2}; letter-spacing:2px; background:transparent;")
        self.target_lbl = QLabel()
        self.target_lbl.setFont(QFont(VAZIR, 10))
        self.target_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.target_lbl.setStyleSheet(f"color:{MUTED}; background:transparent;")
        info_lay.addWidget(self.desc_lbl)
        info_lay.addWidget(self.fingers_lbl)
        info_lay.addWidget(self.target_lbl)
        lay.addWidget(info)

        self.keyboard = PersianKeyboard()
        lay.addWidget(self.keyboard)

        self.typing = TypingWidget()
        self.typing.keyboard_ref = self.keyboard   # wire up
        self.typing.finished.connect(self._done)
        lay.addWidget(self.typing)

        btn = QPushButton("🔄  دوباره تلاش")
        btn.setFont(QFont(VAZIR, 11, QFont.Weight.Medium))
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{ background:{HIGHLIGHT}; color:{TEXT}; border-radius:10px; border:1px solid {BORDER}; }}
            QPushButton:hover {{ background:{ACCENT}; border-color:{ACCENT}; }}
        """)
        btn.clicked.connect(self._start)
        lay.addWidget(btn)

    def load_lesson(self, lesson):
        self.lesson = lesson
        self.title_lbl.setText(f"#{lesson['id']}  {lesson['title']}  –  {lesson['subtitle']}")
        self.desc_lbl.setText(lesson["desc"])
        self.fingers_lbl.setText(lesson["fingers"])
        self.target_lbl.setText(f"🎯 هدف: {lesson['target_wpm']} WPM  ·  دقت {lesson['target_acc']}% به بالا")
        self.keyboard.set_hint_keys(lesson["hint_keys"])
        self._start()
        self.typing.setFocus()

    def _start(self):
        words = random.sample(self.lesson["words"], min(WORDS_PER_ROUND, len(self.lesson["words"])))
        self.typing.load_words(words)
        self.typing.setFocus()

    def _done(self, wpm, acc):
        self.completed.emit(self.lesson["id"], wpm, acc)


# ── Result Screen ────────────────────────────────────────────────────────────
class ResultScreen(QWidget):
    retry       = pyqtSignal()
    next_lesson = pyqtSignal()
    home        = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._particles = []
        self._ptimer = QTimer(self)
        self._ptimer.timeout.connect(self._tick_particles)
        self._passed = False
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(80, 20, 80, 20)
        lay.setSpacing(16)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        brand = MonsterBrand("normal")
        lay.addWidget(brand)

        self.emoji_lbl = QLabel("🎉")
        self.emoji_lbl.setFont(QFont("Segoe UI Emoji", 52))
        self.emoji_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emoji_lbl.setStyleSheet("background:transparent;")
        lay.addWidget(self.emoji_lbl)

        self.title_lbl = QLabel()
        self.title_lbl.setFont(QFont(VAZIR, 22, QFont.Weight.Black))
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_lbl.setStyleSheet(f"color:{TEXT}; background:transparent;")
        lay.addWidget(self.title_lbl)

        # Stats card
        stats = QFrame()
        stats.setStyleSheet(f"QFrame {{ background:{CARD}; border:1px solid {BORDER}; border-radius:20px; }}")
        stats_lay = QHBoxLayout(stats)
        stats_lay.setContentsMargins(50, 20, 50, 20)
        stats_lay.setSpacing(60)

        self.wpm_val = QLabel("–")
        self.wpm_val.setFont(QFont(VAZIR, 40, QFont.Weight.Black))
        self.wpm_val.setStyleSheet(f"color:{FIRE2}; background:transparent;")
        self.wpm_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wlbl = QLabel("کلمه در دقیقه")
        wlbl.setFont(QFont(VAZIR, 10))
        wlbl.setStyleSheet(f"color:{MUTED}; background:transparent;")
        wlbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        wb = QWidget(); wb.setStyleSheet("background:transparent;")
        wblay = QVBoxLayout(wb); wblay.addWidget(self.wpm_val); wblay.addWidget(wlbl)

        self.acc_val = QLabel("–")
        self.acc_val.setFont(QFont(VAZIR, 40, QFont.Weight.Black))
        self.acc_val.setStyleSheet(f"color:{SUCCESS}; background:transparent;")
        self.acc_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        albl = QLabel("دقت تایپ")
        albl.setFont(QFont(VAZIR, 10))
        albl.setStyleSheet(f"color:{MUTED}; background:transparent;")
        albl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ab = QWidget(); ab.setStyleSheet("background:transparent;")
        ablay = QVBoxLayout(ab); ablay.addWidget(self.acc_val); ablay.addWidget(albl)

        stats_lay.addWidget(wb); stats_lay.addWidget(ab)
        lay.addWidget(stats)

        self.feedback_lbl = QLabel()
        self.feedback_lbl.setFont(QFont(VAZIR, 11))
        self.feedback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.feedback_lbl.setStyleSheet(f"color:{MUTED}; background:transparent;")
        self.feedback_lbl.setWordWrap(True)
        lay.addWidget(self.feedback_lbl)

        btns = QHBoxLayout()
        btns.setSpacing(12)
        self.home_btn  = self._btn("🏠 صفحه اصلی", HIGHLIGHT)
        self.retry_btn = self._btn("🔄 دوباره", HIGHLIGHT)
        self.next_btn  = self._btn("درس بعد ►", ACCENT)
        self.home_btn.clicked.connect(self.home)
        self.retry_btn.clicked.connect(self.retry)
        self.next_btn.clicked.connect(self.next_lesson)
        for b in (self.home_btn, self.retry_btn, self.next_btn):
            btns.addWidget(b)
        lay.addLayout(btns)

        footer = QLabel("⚡ code_rah — تایپ مثل یک هیولا")
        footer.setFont(QFont("Consolas", 9))
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color:{MUTED}; background:transparent;")
        lay.addWidget(footer)

    def _btn(self, text, bg):
        b = QPushButton(text)
        b.setFont(QFont(VAZIR, 11, QFont.Weight.Medium))
        b.setFixedHeight(44)
        b.setMinimumWidth(130)
        b.setStyleSheet(f"""
            QPushButton {{ background:{bg}; color:{TEXT}; border-radius:12px; border:1px solid {BORDER}; }}
            QPushButton:hover {{ background:{ACCENT}; border-color:{ACCENT}; }}
        """)
        return b

    def show_result(self, lesson, wpm, acc):
        passed = wpm >= lesson["target_wpm"] and acc >= lesson["target_acc"]
        self._passed = passed
        self.emoji_lbl.setText("🏆" if passed else "💪")
        self.title_lbl.setText("عالی! قبول شدی! 🔥" if passed else "ادامه بده، می‌تونی! 💪")
        self.title_lbl.setStyleSheet(f"color:{SUCCESS if passed else WARNING}; background:transparent;")
        self.wpm_val.setText(str(int(wpm)))
        self.acc_val.setText(f"{int(acc)}%")

        if passed:
            fb = f"🔥 هدف {lesson['target_wpm']} WPM با دقت {lesson['target_acc']}%+ رو رد کردی! درس بعدی باز شد!"
            self.next_btn.setEnabled(True)
            self.next_btn.setStyleSheet(f"""
                QPushButton {{ background:{ACCENT}; color:{TEXT}; border-radius:12px; border:1px solid {ACCENT}; }}
                QPushButton:hover {{ background:{FIRE2}; border-color:{FIRE2}; }}
            """)
        else:
            tips = []
            if wpm < lesson["target_wpm"]:
                tips.append(f"سرعت رو به {lesson['target_wpm']} WPM برسون")
            if acc < lesson["target_acc"]:
                tips.append(f"دقت رو بالاتر از {lesson['target_acc']}% نگه دار")
            fb = "  ·  ".join(tips) if tips else "تلاش کن بهتر بشی!"
            self.next_btn.setEnabled(False)
            self.next_btn.setStyleSheet(f"""
                QPushButton {{ background:{MUTED2}; color:{MUTED}; border-radius:12px; border:1px solid {MUTED2}; }}
            """)

        self.feedback_lbl.setText(fb)
        if passed:
            self._spawn_particles()

    def _spawn_particles(self):
        import random as rr
        self._particles = [
            {"x": rr.uniform(0.1, 0.9), "y": rr.uniform(0.0, 0.4),
             "vy": rr.uniform(0.003, 0.007), "vx": rr.uniform(-0.002, 0.002),
             "color": rr.choice([FIRE1, FIRE2, FIRE3, WARNING, SUCCESS]),
             "size": rr.randint(5, 13), "life": 1.0}
            for _ in range(50)
        ]
        self._ptimer.start(28)

    def _tick_particles(self):
        alive = []
        for pt in self._particles:
            pt["y"] += pt["vy"]
            pt["x"] += pt["vx"]
            pt["life"] -= 0.016
            if pt["life"] > 0 and pt["y"] < 1.2:
                alive.append(pt)
        self._particles = alive
        self.update()
        if not alive:
            self._ptimer.stop()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self._particles: return
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        for pt in self._particles:
            c = QColor(pt["color"])
            c.setAlphaF(pt["life"])
            p.setBrush(c)
            p.setPen(Qt.PenStyle.NoPen)
            px, py = int(pt["x"] * w), int(pt["y"] * h)
            p.drawEllipse(px, py, pt["size"], pt["size"])
        p.end()

class AnimatedBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(850, 600)
        self.pixmap = QPixmap(self.width(), self.height())
        self.pixmap.fill(Qt.GlobalColor.black)

        self.angle = 0
        self.length = 0
        self.x, self.y = 0, 150
        self.step = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_drawing)
        self.timer.start(30)

        self.label = QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width(), self.height())
        self.label.move(0, 0)

    def update_drawing(self):
        painter = QPainter(self.pixmap)
        painter.setPen(QPen(QColor("green"), 1))

        rad = math.radians(self.angle)
        dx = self.length * math.cos(rad)
        dy = self.length * math.sin(rad)

        cx, cy = self.width() // 2, self.height() // 1.5

        painter.drawLine(cx + self.x, cy - self.y, cx + self.x + dx, cy - self.y - dy)

        self.x += dx
        self.y += dy

        self.length += 3
        self.angle += 1
        self.step += 1

        painter.end()
        self.label.setPixmap(self.pixmap)

        if self.step >= 204:
            self.timer.stop()

    def resizeEvent(self, event):
        self.pixmap = self.pixmap.scaled(self.width(), self.height())
        self.label.setPixmap(self.pixmap)
# ── Main Window ──────────────────────────────────────────────────────────────
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.progress = load_progress()
        self.current_lesson = None
        self.setWindowTitle("⚡ TyplOf — آموزش تایپ فارسی ۱۰ انگشت")
        self.resize(1280, 800)

        # === پس‌زمینه متحرک جدید (Turtle) ===
        self.bg_animated = AnimatedBackground(self)
        self.bg_animated.lower()
        self.bg_animated.show()

        self._bg = GlowBg(self)
        self._bg.resize(self.size())
        self._bg.lower()

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        self.setCentralWidget(container)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")

        self.lesson_screen = LessonScreen()
        self.result_screen = ResultScreen()
        self.lesson_screen.back.connect(self._go_home)
        self.lesson_screen.completed.connect(self._show_result)
        self.result_screen.retry.connect(self._retry)
        self.result_screen.next_lesson.connect(self._next_lesson)
        self.result_screen.home.connect(self._go_home)

        self._hw = None
        self._build_home()
        self.stack.addWidget(self.lesson_screen)
        self.stack.addWidget(self.result_screen)

        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.stack)

        self.setStyleSheet(f"QMainWindow {{ background:{BG}; }}")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._bg.resize(self.size())
        # تغییر اندازه‌ی پس‌زمینه متحرک هماهنگ با پنجره
        self.bg_animated.setFixedSize(self.width(), self.height())
        self.bg_animated.pixmap = QPixmap(self.width(), self.height())
        self.bg_animated.pixmap.fill(Qt.GlobalColor.black)
        self.bg_animated.label.resize(self.width(), self.height())

    def _build_home(self):
        if self._hw:
            self.stack.removeWidget(self._hw)
            self._hw.deleteLater()
        hw = HomeScreen(self.progress)
        hw.lesson_selected.connect(self._start_lesson)
        self.stack.insertWidget(0, hw)
        self._hw = hw
        self.stack.setCurrentIndex(0)

    def _start_lesson(self, lid):
        lesson = next(l for l in LESSONS if l["id"] == lid)
        self.current_lesson = lesson
        self.lesson_screen.load_lesson(lesson)
        self._animate_to(1)

    def _show_result(self, lid, wpm, acc):
        lesson = next(l for l in LESSONS if l["id"] == lid)
        passed = wpm >= lesson["target_wpm"] and acc >= lesson["target_acc"]
        if passed:
            prev = self.progress.get(lid, {})
            self.progress[lid] = {
                "done": True,
                "wpm": max(int(wpm), prev.get("wpm", 0)),
                "acc": int(acc)
            }
            save_progress(self.progress)
        self.result_screen.show_result(lesson, wpm, acc)
        self._animate_to(2)

    def _retry(self):
        self._animate_to(1)
        self.lesson_screen._start()
        self.lesson_screen.typing.setFocus()

    def _next_lesson(self):
        nid = self.current_lesson["id"] + 1
        if nid <= len(LESSONS):
            self._start_lesson(nid)
        else:
            self._go_home()

    def _go_home(self):
        self._build_home()

    def _animate_to(self, index):
        widget = self.stack.widget(index)
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.stack.setCurrentIndex(index)
        anim.start()
        self._anim = anim


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    load_fonts()
    app.setFont(QFont(VAZIR, 11))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

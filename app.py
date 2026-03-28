import streamlit as st
from groq import Groq
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import io, os, smtplib, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ══════════════════════════════════════════════════════════════
#  CONFIG
# ══════════════════════════════════════════════════════════════
GMAIL_USER      = "Wijdan.psyc@gmail.com"
GMAIL_PASS      = "rias eeul lyuu stce"
RECIPIENT_EMAIL = "Wijdan.psyc@gmail.com"
LOGO_PATH       = os.path.join(os.path.dirname(__file__), "logo.png")

DEEP_BLUE  = "#3B5FC0"
MID_BLUE   = "#6B8ED6"
LOGO_BLUE  = "#A1B6F3"
LIGHT_BG   = "#F0F4FF"
DARK_BLUE  = "#1B2A4A"

CLINIC_BLUE_RGB = RGBColor(0x3B, 0x5F, 0xC0)
DARK_BLUE_RGB   = RGBColor(0x1B, 0x2A, 0x4A)
LOGO_BLUE_RGB   = RGBColor(0xA1, 0xB6, 0xF3)

# ══════════════════════════════════════════════════════════════
#  CONNERS CPRS-R:L — 80 ITEMS  (English + Arabic)
# ══════════════════════════════════════════════════════════════
ITEMS_EN = [
    "Angry and resentful",                                                            # 1
    "Difficulty doing or completing homework",                                        # 2
    "Is always 'on the go' or acts as if driven by a motor",                         # 3
    "Timid, easily frightened",                                                       # 4
    "Everything must be just so",                                                     # 5
    "Has no friends",                                                                 # 6
    "Stomach aches",                                                                  # 7
    "Fights",                                                                         # 8
    "Avoids or has difficulties engaging in tasks that require sustained mental effort", # 9
    "Has difficulty sustaining attention in tasks or play activities",                # 10
    "Argues with adults",                                                             # 11
    "Fails to complete assignments",                                                  # 12
    "Hard to control in malls or while grocery shopping",                             # 13
    "Afraid of people",                                                               # 14
    "Keeps checking things over and over again",                                      # 15
    "Loses friends quickly",                                                          # 16
    "Aches and Pains",                                                                # 17
    "Restless or overactive",                                                         # 18
    "Has trouble concentrating in class",                                             # 19
    "Does not seem to listen to what is being said",                                  # 20
    "Loses temper",                                                                   # 21
    "Needs close supervision to get through assignments",                             # 22
    "Runs about or climbs excessively in inappropriate situations",                   # 23
    "Afraid of new situations",                                                       # 24
    "Fussy about cleanliness",                                                        # 25
    "Does not know how to make friends",                                              # 26
    "Gets aches and pains or stomachaches before school",                             # 27
    "Excitable, impulsive",                                                           # 28
    "Does not follow through on instructions and fails to finish schoolwork",         # 29
    "Has difficulty organising tasks and activities",                                 # 30
    "Irritable",                                                                      # 31
    "Restless in the 'squirmy sense'",                                                # 32
    "Afraid of being alone",                                                          # 33
    "Things must be done the same way every time",                                    # 34
    "Does not get invited over to friends' houses",                                   # 35
    "Headaches",                                                                      # 36
    "Fails to finish things he/she starts",                                           # 37
    "Inattentive, easily distracted",                                                 # 38
    "Talks excessively",                                                              # 39
    "Actively defies or refuses to comply with adults' requests",                     # 40
    "Fails to give close attention to detail or makes careless mistakes",             # 41
    "Has difficulty waiting in lines or awaiting turn in group situations",           # 42
    "Has a lot of fears",                                                             # 43
    "Has rituals that he/she must go through",                                        # 44
    "Distractibility or attention span problem",                                      # 45
    "Complains about being sick even when nothing is wrong",                          # 46
    "Temper outbursts",                                                               # 47
    "Gets distracted when given instructions to do something",                        # 48
    "Interrupts or intrudes on others (butts into conversations or games)",           # 49
    "Forgetful in daily activities",                                                  # 50
    "Cannot grasp arithmetic",                                                        # 51
    "Will run around between mouthfuls at meals",                                     # 52
    "Afraid of the dark, animals or bugs",                                            # 53
    "Sets very high goals for self",                                                  # 54
    "Fidgets with hands or feet or squirms in seat",                                  # 55
    "Short attention span",                                                           # 56
    "Touchy or easily annoyed by others",                                             # 57
    "Has sloppy handwriting",                                                         # 58
    "Has difficulty playing or engaging in leisure activities quietly",               # 59
    "Shy, withdrawn",                                                                 # 60
    "Blames others for his/her mistakes or misbehaviour",                             # 61
    "Fidgeting",                                                                      # 62
    "Messy or disorganised at home or school",                                        # 63
    "Gets upset if someone rearranges his/her things",                                # 64
    "Clings to parents or other adults",                                              # 65
    "Disturbs other children",                                                        # 66
    "Deliberately does things that annoy other people",                               # 67
    "Demands must be met immediately — easily frustrated",                            # 68
    "Only attends if it is something he/she is very interested in",                   # 69
    "Spiteful or vindictive",                                                         # 70
    "Loses things necessary for tasks (pencils, books, tools or toys)",               # 71
    "Feels inferior to others",                                                       # 72
    "Seems tired or slowed down at times",                                            # 73
    "Spelling is poor",                                                               # 74
    "Cries often and easily",                                                         # 75
    "Leaves seat in classroom or where remaining seated is expected",                 # 76
    "Mood changes quickly and drastically",                                           # 77
    "Easily frustrated efforts",                                                      # 78
    "Easily distracted by extraneous stimuli",                                        # 79
    "Blurts out answers before questions have been completed",                        # 80
]

ITEMS_AR = [
    "مستاء وغاضب",                                                                    # 1
    "يعاني من صعوبة في أداء الواجب أو إنهاءه",                                       # 2
    "دائما يريد الحركة أو يتصرف كأنه مدفوع بموتور",                                   # 3
    "خجول ـ يخاف بسهولة",                                                            # 4
    "كل شيء يجب أن يكون دقيقاً ومضبوطاً",                                            # 5
    "ليس لديه أصدقاء",                                                               # 6
    "يعاني من أمراض المعدة",                                                          # 7
    "يتخاتق ويتشاجر",                                                                 # 8
    "يتجنب أو لديه صعوبة في عمل شيء يحتاج إلى تركيز ذهني (واجب المدرس)",             # 9
    "يعاني من صعوبة في التركيز فترة طويلة في الأعمال أو اللعب",                      # 10
    "يجادل مع الكبار",                                                               # 11
    "يفشل في إنهاء مهماته أو واجباته",                                                # 12
    "صعب السيطرة عليه في الأسواق التجارية أو أثناء شراء احتياجات المنزل",             # 13
    "يخاف من الناس",                                                                  # 14
    "يتأكد من الأشياء مراراً وتكراراً",                                               # 15
    "يخسر أصحابه بسرعة",                                                             # 16
    "عنده أوجاع وآلام",                                                              # 17
    "لا يهدأ وكثير النشاط والحركة غير مستقر",                                         # 18
    "يعاني من مشاكل في التركيز في الفصل",                                            # 19
    "لا يستمع لما يقال إليه",                                                         # 20
    "يفقد أعصابه",                                                                   # 21
    "يحتاج إلى إشراف دائم لينتهي من واجباته",                                        # 22
    "يجري أو يتسلق كثيراً في موقف لا يصح فيه هذا التصرف",                            # 23
    "يخاف من المواقف الجديدة",                                                        # 24
    "يهتم بالنظافة إلى حد مزعج أو كبير",                                             # 25
    "لا يعرف كيف يعمل صداقات",                                                       # 26
    "يعاني من أوجاع وآلام أو ألم بالمعدة قبل الذهاب للمدرسة",                        # 27
    "سهل الاستثارة ومندفع",                                                           # 28
    "لا يتبع التعليمات ويفشل في إنهاء واجباته في العمل أو الدراسة",                   # 29
    "يعاني من صعوبة في تنظيم الواجبات والنشاطات",                                   # 30
    "متهيج",                                                                          # 31
    "كثير الحركة أو قلق",                                                            # 32
    "يخاف من البقاء بمفرده",                                                          # 33
    "لابد من عمل الأشياء بنفس الطريقة كل مرة",                                       # 34
    "لا يدعوه أحد من أصدقائه لزيارته بمنزله",                                        # 35
    "يعاني من الصداع",                                                               # 36
    "يفشل في إنهاء الأشياء التي بدأها",                                              # 37
    "قليل التركيز، سهل أن تتشتت تركيزه",                                             # 38
    "يتكلم كثيراً",                                                                   # 39
    "يعاند أو يرفض بقوة أن يلتزم بطلبات الكبار",                                     # 40
    "يفشل أن يعطي إنتباهه للتفاصيل ويرتكب أخطاء في المدرسة أو العمل أو أي نشاط آخر", # 41
    "يعاني من صعوبة في الإنتظار في الطابور أو إنتظار دوره في اللعب أو المواقف الجماعية", # 42
    "يعاني من مخاوف كثيرة",                                                          # 43
    "لديه طقوس لابد أن يؤديها",                                                      # 44
    "تشتت تركيزه ومدى إنتباهه يعتبر مشكلة",                                         # 45
    "يشتكي من أنه مريض بالرغم من أنه لا يوجد به شيء",                               # 46
    "مزاجه حاد وينفجر بعصبية",                                                       # 47
    "يتشتت تركيزه أثناء إعطائه تعليمات لعمل شيء",                                   # 48
    "يقاطع أو يتدخل في أحاديث الآخرين أو ألعابهم",                                  # 49
    "كثير النسيان في نشاطه اليومي",                                                  # 50
    "لا يستطيع فهم الحساب (الرياضيات)",                                              # 51
    "في وقت الأكل كثير الجري بين كل ملعقة والأخرى",                                 # 52
    "يخاف من الظلام، الحيوانات والحشرات",                                            # 53
    "يضع لنفسه أهداف عالية",                                                         # 54
    "يفرك ويتمالك بيديه وقدميه ويفرك في الكرسي",                                    # 55
    "مدى تركيز قليل",                                                                # 56
    "يتضايق بسهولة مع الآخرين وسريع الغضب (حمقي)",                                  # 57
    "خطه سيء",                                                                       # 58
    "يعاني من صعوبة في اللعب أو الإنشغال في أي نشاط مسلي بهدوء",                   # 59
    "خجول ومنطوي",                                                                   # 60
    "يلوم الآخرين على أخطائه أو سوء تصرفه",                                         # 61
    "كثير الململة والفرك",                                                            # 62
    "فوضوي، غير منظم بالمدرسة والبيت",                                               # 63
    "يتضايق إذا نظم أحدهم أشياءه",                                                   # 64
    "يتعلق بالأبوين أو أحد الكبار",                                                  # 65
    "يزعج الأطفال الآخرين",                                                          # 66
    "يتعمد عمل أشياء تضايق الآخرين",                                                 # 67
    "طلباته لابد أن تجاب في الحال ـ سهل الإحباط",                                   # 68
    "لا يركز في شيء إلا لو كان مهتماً به",                                          # 69
    "حقود، كياد، انتقامي",                                                            # 70
    "يفقد الأشياء اللازمة لتأدية واجباته ونشاطاته (أقلام، كتب، أدوات، واجبات مدرسية)", # 71
    "يشعر بأنه أقل من الآخرين",                                                      # 72
    "يبدو متعباً أو بطيء طوال الوقت",                                                # 73
    "لا يستطيع الهجاء (لا يحفظ الأحرف في الإملاء)",                                # 74
    "يبكي بسهولة وبكثرة",                                                            # 75
    "يترك كرسيه في الفصل أو مواقف أخرى لابد فيها من الجلوس",                        # 76
    "يتغير مزاجه بسرعة تغيراً كبيراً",                                              # 77
    "يحبط بسهولة بعد محاولة إنجاز أي شيء",                                          # 78
    "يسهل أن يتشتت تركيزه بأي مؤثرات خارجية",                                       # 79
    "ينزلق في الإجابة بسرعة قبل إنتهاء السؤال",                                     # 80
]

# ══════════════════════════════════════════════════════════════
#  SCORING KEY  (item numbers → subscales A–N)
#  Source: Conners CPRS-R:L scoring key
# ══════════════════════════════════════════════════════════════
SUBSCALES = {
    "A": {
        "name_en": "Oppositional",
        "name_ar": "العناد",
        "items": [1, 8, 11, 21, 40, 61, 67, 70],
        "color": "#E53935",
    },
    "B": {
        "name_en": "Cognitive Problems / Inattention",
        "name_ar": "مشكلات معرفية / نقص انتباه",
        "items": [2, 9, 10, 12, 19, 29, 30, 37, 41, 45, 48, 50, 51, 56],
        "color": "#8E24AA",
    },
    "C": {
        "name_en": "Hyperactivity",
        "name_ar": "فرط الحركة",
        "items": [3, 18, 23, 28, 32, 39, 42, 49, 52, 55, 59, 62, 76, 80],
        "color": "#F4511E",
    },
    "D": {
        "name_en": "Anxious-Shy",
        "name_ar": "القلق / الخجل",
        "items": [4, 14, 24, 33, 43, 53, 60, 65],
        "color": "#039BE5",
    },
    "E": {
        "name_en": "Perfectionism",
        "name_ar": "الإتقان",
        "items": [5, 15, 25, 34, 44, 54, 64],
        "color": "#00897B",
    },
    "F": {
        "name_en": "Social Problems",
        "name_ar": "مشكلات اجتماعية",
        "items": [6, 16, 26, 35, 72],
        "color": "#FB8C00",
    },
    "G": {
        "name_en": "Psychosomatic",
        "name_ar": "المشكلات النفس جسمية",
        "items": [7, 17, 27, 36, 46],
        "color": "#6D4C41",
    },
    "H": {
        "name_en": "ADHD Index",
        "name_ar": "دليل فرط الحركة ونقص الانتباه",
        "items": [13, 20, 22, 38, 41, 45, 48, 55, 56, 63, 68, 79],
        "color": "#C62828",
    },
    "I": {
        "name_en": "CGI: Restless-Impulsive",
        "name_ar": "دليل الاستثارة والاندفاعية",
        "items": [3, 18, 22, 28, 32, 38, 39, 42, 45, 55, 62, 79, 80],
        "color": "#AD1457",
    },
    "J": {
        "name_en": "CGI: Emotional Lability",
        "name_ar": "العاطفة",
        "items": [21, 47, 57, 75, 77],
        "color": "#1565C0",
    },
    "K": {
        "name_en": "CGI: Total",
        "name_ar": "المؤشر العام",
        "items": [3, 6, 9, 10, 12, 13, 18, 19, 20, 21, 22, 28, 31, 32,
                  38, 39, 42, 45, 47, 48, 49, 55, 57, 62, 75, 77, 79, 80],
        "color": "#1B5E20",
    },
    "L": {
        "name_en": "DSM-IV: Inattentive",
        "name_ar": "نقص الانتباه DSM-IV",
        "items": [9, 10, 12, 20, 29, 38, 41, 45, 50, 56, 71, 79],
        "color": "#4527A0",
    },
    "M": {
        "name_en": "DSM-IV: Hyperactive-Impulsive",
        "name_ar": "فرط الحركة والاندفاعية DSM-IV",
        "items": [3, 18, 23, 28, 32, 39, 42, 49, 52, 55, 59, 62, 76, 80],
        "color": "#BF360C",
    },
    "N": {
        "name_en": "DSM-IV: Total",
        "name_ar": "مختلط DSM-IV",
        "items": [3, 9, 10, 12, 18, 20, 23, 28, 29, 32, 38, 39, 41, 42,
                  45, 49, 50, 52, 55, 56, 59, 62, 71, 76, 79, 80],
        "color": "#33691E",
    },
}

# T-score interpretation thresholds
def get_level_en(t):
    if t >= 70:   return "Markedly Atypical — Significant Concern"
    elif t >= 65: return "Mildly Atypical — Likely Concern"
    elif t >= 60: return "Slightly Atypical — Worth Monitoring"
    elif t >= 40: return "Average Range"
    else:         return "Below Average"

def get_level_ar(t):
    if t >= 70:   return "ملحوظ بشكل واضح — مصدر قلق كبير"
    elif t >= 65: return "ملحوظ بشكل خفيف — مصدر قلق محتمل"
    elif t >= 60: return "ملحوظ قليلاً — يستحق المتابعة"
    elif t >= 40: return "ضمن المتوسط الطبيعي"
    else:         return "أقل من المتوسط"

def get_bar_color(t):
    if t >= 70:   return "#D32F2F"
    elif t >= 65: return "#F57C00"
    elif t >= 60: return "#FBC02D"
    elif t >= 40: return "#388E3C"
    else:         return "#1976D2"

# ══════════════════════════════════════════════════════════════
#  SCORING  (raw → approximate T-score via linear scaling)
# ══════════════════════════════════════════════════════════════
# Approximate normative means and SDs (Conners, 1997 — combined reference)
NORMS = {
    "A": (6.8,  4.2),
    "B": (13.5, 7.8),
    "C": (10.2, 6.5),
    "D": (5.8,  4.0),
    "E": (5.2,  3.8),
    "F": (3.5,  2.8),
    "G": (2.8,  2.5),
    "H": (11.0, 6.8),
    "I": (13.5, 7.5),
    "J": (5.5,  3.9),
    "K": (35.0, 16.0),
    "L": (11.2, 6.8),
    "M": (10.2, 6.5),
    "N": (18.5, 10.5),
}

def raw_to_t(raw, scale_key):
    mean, sd = NORMS[scale_key]
    if sd == 0: return 50
    t = 50 + 10 * (raw - mean) / sd
    return max(20, min(90, round(t)))

def compute_scores(responses: dict) -> dict:
    results = {}
    for key, info in SUBSCALES.items():
        raw = sum(responses.get(i, 0) for i in info["items"])
        t   = raw_to_t(raw, key)
        results[key] = {"raw": raw, "t": t, "max_raw": len(info["items"]) * 3}
    return results

# ══════════════════════════════════════════════════════════════
#  CHART GENERATION
# ══════════════════════════════════════════════════════════════
def make_bar_chart(scores: dict, lang: str) -> bytes:
    labels  = []
    t_vals  = []
    colors_ = []

    for key in ["A","B","C","D","E","F","G","H","I","J","K","L","M","N"]:
        info = SUBSCALES[key]
        t    = scores[key]["t"]
        labels.append(info["name_en"] if lang=="en" else info["name_ar"])
        t_vals.append(t)
        colors_.append(get_bar_color(t))

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor('#F8F9FF')
    ax.set_facecolor('#F8F9FF')

    y_pos = np.arange(len(labels))
    bars  = ax.barh(y_pos, t_vals, color=colors_, edgecolor='white',
                    linewidth=0.8, height=0.65)

    # Reference lines
    for x_val, lbl, col in [(40,'T=40','#388E3C'), (60,'T=60','#FBC02D'),
                              (65,'T=65','#F57C00'), (70,'T=70','#D32F2F')]:
        ax.axvline(x=x_val, color=col, linestyle='--', linewidth=1.2,
                   alpha=0.7, label=lbl)

    # Value labels on bars
    for bar_, val in zip(bars, t_vals):
        ax.text(bar_.get_width() + 0.5, bar_.get_y() + bar_.get_height()/2,
                str(val), va='center', ha='left', fontsize=9, fontweight='bold',
                color='#1B2A4A')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9.5,
                       fontfamily='DejaVu Sans')
    ax.set_xlim(20, 95)
    ax.set_xlabel('T-Score', fontsize=11, fontweight='bold', color='#1B2A4A')
    title = "Conners' CPRS-R:L — T-Score Profile" if lang=="en" else "مقياس كونرز — الدرجات التائية للمقاييس الفرعية"
    ax.set_title(title, fontsize=13, fontweight='bold', color='#1B2A4A', pad=14)
    ax.legend(loc='lower right', fontsize=8.5, framealpha=0.7)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='x', linestyle=':', alpha=0.5)

    # Shade concern zone
    ax.axvspan(70, 95, alpha=0.06, color='#D32F2F', label='_nolegend_')
    ax.axvspan(65, 70, alpha=0.05, color='#F57C00', label='_nolegend_')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()

def make_pie_chart(responses: dict) -> bytes:
    counts = [0, 0, 0, 0]
    for v in responses.values():
        counts[v] += 1
    labels  = ['0 — Not at all', '1 — Just a little', '2 — Pretty much', '3 — Very much']
    colors_ = ['#388E3C', '#FBC02D', '#F57C00', '#D32F2F']
    fig, ax = plt.subplots(figsize=(6, 4.5))
    fig.patch.set_facecolor('#F8F9FF')
    wedges, texts, autotexts = ax.pie(
        counts, labels=labels, colors=colors_,
        autopct='%1.0f%%', startangle=90,
        wedgeprops={'edgecolor':'white','linewidth':1.5}
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_fontweight('bold')
    ax.set_title('Response Distribution', fontsize=11, fontweight='bold', color='#1B2A4A')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# ══════════════════════════════════════════════════════════════
#  GROQ REPORT
# ══════════════════════════════════════════════════════════════
def build_score_block(scores):
    lines = []
    for key in "ABCDEFGHIJKLMN":
        info = SUBSCALES[key]
        s    = scores[key]
        lines.append(
            f"  {key}. {info['name_en']}: Raw={s['raw']}/{s['max_raw']}, T={s['t']} — {get_level_en(s['t'])}"
        )
    return "\n".join(lines)

def generate_report_en(child_name, age, gender, rater, scores):
    score_block = build_score_block(scores)
    elevated = [k for k in "ABCDEFGHIJKLMN" if scores[k]["t"] >= 65]
    prompt = f"""You are a licensed child psychologist writing a professional CPRS-R:L assessment report.

CHILD: {child_name} | AGE: {age} | GENDER: {gender} | RATER: {rater}
ASSESSMENT: Conners' Parent Rating Scale – Revised: Long Version (CPRS-R:L)
DATE: {date.today().strftime('%B %d, %Y')}

SUBSCALE T-SCORES (T≥65 = clinically significant; T≥70 = markedly atypical):
{score_block}

ELEVATED SCALES (T≥65): {', '.join(elevated) if elevated else 'None'}

IMPORTANT RULES:
- Do NOT diagnose. State findings as hypotheses requiring clinical judgment.
- Use formal clinical language.
- Be specific to the T-scores above.
- No markdown symbols (**, ##, ---).
- Section titles: ALL CAPS numbered. Example: 1. REFERRAL & ASSESSMENT OVERVIEW

REPORT STRUCTURE:

CONNERS' PARENT RATING SCALE — CLINICAL REPORT
Child | {child_name}
Age | {age}  |  Gender | {gender}
Rater | {rater}
Date | {date.today().strftime('%B %d, %Y')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CLINICAL SUMMARY
3–5 sentences: present the overall profile, noting most elevated scales and clinical significance.

1. REFERRAL & ASSESSMENT OVERVIEW
Instrument description, purpose, administration context, rating period (past month).

2. SUBSCALE PROFILE ANALYSIS
For each scale rated T≥60, write a dedicated paragraph: T-score, behavioral correlates, clinical significance.
For scales T<60: one brief line noting within-normal-limits finding.

3. DSM-IV SYMPTOM SUBSCALES (L, M, N)
Interpret the three DSM-IV symptom subscales and their implications for diagnostic consideration.

4. CLINICAL GLOBAL INDEX (H, I, J, K)
Interpret the CGI scales. Discuss overall severity of behavioral concerns.

5. STRENGTHS & PROTECTIVE FACTORS
Identify subscales in the average or below-average range as areas of relative strength.

6. INTEGRATED CLINICAL IMPRESSIONS
Synthesize the profile. What overall pattern emerges? What are the primary areas of concern?

7. RECOMMENDATIONS
Evidence-based recommendations for intervention, monitoring, referral, or further assessment.

8. SUMMARY
One paragraph suitable for clinical records:
"According to the CPRS-R:L completed by {rater}, {child_name} (age {age}) presents with..."
"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        max_tokens=3500
    )
    return r.choices[0].message.content.strip()

def generate_report_ar(child_name, age, gender, rater, scores):
    lines = []
    for key in "ABCDEFGHIJKLMN":
        info = SUBSCALES[key]
        s    = scores[key]
        lines.append(
            f"  {key}. {info['name_ar']}: خام={s['raw']}/{s['max_raw']}, تائي={s['t']} — {get_level_ar(s['t'])}"
        )
    score_block_ar = "\n".join(lines)
    elevated_ar = [SUBSCALES[k]["name_ar"] for k in "ABCDEFGHIJKLMN" if scores[k]["t"] >= 65]

    prompt = f"""أنت طبيب نفسي للأطفال تكتب تقريراً سريرياً احترافياً لمقياس كونرز للوالدين (النسخة المراجعة الطويلة).

الطفل: {child_name} | السن: {age} | النوع: {gender} | المُقيِّم: {rater}
المقياس: مقياس كونرز للوالدين — نسخة مراجعة طويلة (CPRS-R:L)
التاريخ: {date.today().strftime('%Y/%m/%d')}

الدرجات التائية للمقاييس الفرعية (T≥65 = ذو دلالة سريرية؛ T≥70 = ملحوظ بشكل واضح):
{score_block_ar}

المقاييس المرتفعة (T≥65): {', '.join(elevated_ar) if elevated_ar else 'لا يوجد'}

قواعد صارمة:
- لا تضع تشخيصاً. أشر إلى النتائج كفرضيات تحتاج إلى حكم سريري.
- استخدم لغة سريرية رسمية بالعربية الكاملة. لا إنجليزية إلا للاختصارات الطبية (CPRS-R:L, DSM-IV, ADHD, CGI).
- لا رموز markdown (**, ##, ---).
- عناوين الأقسام: أرقام عربية + عنوان. مثال: ١. نظرة عامة على التقييم
- اتجاه النص: من اليمين إلى اليسار.

هيكل التقرير:

تقرير مقياس كونرز للوالدين — التقرير السريري
الطفل | {child_name}
السن | {age}  |  النوع | {gender}
المُقيِّم | {rater}
التاريخ | {date.today().strftime('%Y/%m/%d')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ملخص سريري
٣–٥ جمل: تلخيص المقياس العام، المقاييس الأكثر ارتفاعاً، والدلالة السريرية.

١. نظرة عامة على التقييم
وصف الأداة، الغرض منها، سياق التطبيق، فترة التقييم (الشهر الماضي).

٢. تحليل المقاييس الفرعية
لكل مقياس بدرجة T≥60: فقرة مخصصة (الدرجة التائية، المظاهر السلوكية، الدلالة السريرية).
للمقاييس T<60: سطر واحد موجز يشير إلى الدرجة ضمن الحدود الطبيعية.

٣. مقاييس أعراض DSM-IV (L, M, N)
تفسير المقاييس الثلاثة وانعكاساتها على الاعتبارات التشخيصية.

٤. المؤشر السريري العام (H, I, J, K)
تفسير مقاييس CGI. مناقشة مستوى حدة المخاوف السلوكية.

٥. نقاط القوة والعوامل الوقائية
تحديد المقاييس ضمن المتوسط أو أقل منه كمناطق قوة نسبية.

٦. الانطباعات السريرية المتكاملة
تركيب الصورة الكلية. ما النمط العام؟ ما المجالات الأساسية للقلق؟

٧. التوصيات
توصيات مبنية على الأدلة للتدخل، المتابعة، الإحالة، أو التقييم الإضافي.

٨. الملخص
فقرة واحدة مناسبة للسجلات السريرية.
"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        max_tokens=3500
    )
    return r.choices[0].message.content.strip()

# ══════════════════════════════════════════════════════════════
#  WORD DOC BUILDER
# ══════════════════════════════════════════════════════════════
def build_word_report(report_text, scores, bar_chart_bytes, pie_chart_bytes,
                      child_name, age, gender, rater, lang):
    is_rtl = (lang == "ar")
    doc = Document()

    for sec_ in doc.sections:
        sec_.top_margin    = Cm(2.0)
        sec_.bottom_margin = Cm(2.0)
        sec_.left_margin   = Cm(2.2)
        sec_.right_margin  = Cm(2.2)

    # Page border
    for sec_ in doc.sections:
        sp = sec_._sectPr
        pb = OxmlElement('w:pgBorders')
        pb.set(qn('w:offsetFrom'), 'page')
        for side in ('top','left','bottom','right'):
            b = OxmlElement(f'w:{side}')
            b.set(qn('w:val'),'single'); b.set(qn('w:sz'),'10')
            b.set(qn('w:space'),'24');   b.set(qn('w:color'),'3B5FC0')
            pb.append(b)
        sp.append(pb)

    # Footer
    for sec_ in doc.sections:
        ft = sec_.footer
        fp = ft.paragraphs[0] if ft.paragraphs else ft.add_paragraph()
        fp.clear(); fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_ = fp.add_run()
        r_.font.size = Pt(9); r_.font.color.rgb = CLINIC_BLUE_RGB
        for tag, text in [('begin',None),(None,' PAGE '),('end',None)]:
            if tag:
                el = OxmlElement('w:fldChar'); el.set(qn('w:fldCharType'), tag); r_._r.append(el)
            else:
                it = OxmlElement('w:instrText'); it.text = text; r_._r.append(it)

    def set_rtl_para(p):
        if is_rtl:
            pPr = p._p.get_or_add_pPr()
            pPr.append(OxmlElement("w:bidi"))
            jc = OxmlElement("w:jc"); jc.set(qn("w:val"),"right"); pPr.append(jc)

    def add_para(text, bold=False, size=11, color=None, space_before=0,
                 space_after=4, alignment=None, keep_next=False):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after  = Pt(space_after)
        if keep_next: p.paragraph_format.keep_with_next = True
        set_rtl_para(p)
        if alignment: p.alignment = alignment
        r_ = p.add_run(text)
        r_.font.size = Pt(size); r_.font.name = "Arial"; r_.font.bold = bold
        if color: r_.font.color.rgb = color
        return p

    def add_section_title(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after  = Pt(3)
        p.paragraph_format.keep_with_next = True
        set_rtl_para(p)
        r_ = p.add_run(text.strip())
        r_.font.size = Pt(13); r_.font.name = "Arial"
        r_.font.bold = True; r_.font.color.rgb = CLINIC_BLUE_RGB
        pPr  = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bot  = OxmlElement('w:bottom')
        bot.set(qn('w:val'),'single'); bot.set(qn('w:sz'),'6')
        bot.set(qn('w:space'),'2');    bot.set(qn('w:color'),'3B5FC0')
        pBdr.append(bot); pPr.append(pBdr)

    def make_table():
        t = doc.add_table(rows=0, cols=2)
        t.style = 'Table Grid'
        try:
            tPr = t._tbl.tblPr
            if is_rtl:
                bv = OxmlElement('w:bidiVisual'); tPr.append(bv)
            tW = OxmlElement('w:tblW')
            tW.set(qn('w:w'),'9026'); tW.set(qn('w:type'),'dxa'); tPr.append(tW)
            tg = OxmlElement('w:tblGrid')
            for w in [3000, 6026]:
                gc = OxmlElement('w:gridCol'); gc.set(qn('w:w'), str(w)); tg.append(gc)
            t._tbl.insert(0, tg)
        except: pass
        return t

    def add_row(table, field, value, header=False):
        row  = table.add_row()
        trPr = row._tr.get_or_add_trPr()
        cs   = OxmlElement('w:cantSplit'); cs.set(qn('w:val'),'1'); trPr.append(cs)
        if is_rtl:
            bidi_ = OxmlElement('w:bidi'); trPr.append(bidi_)

        for idx, (cell, txt, bold_) in enumerate([
            (row.cells[0], field, True),
            (row.cells[1], value, header)
        ]):
            cell.text = ""
            p = cell.paragraphs[0]
            if is_rtl:
                pPr = p._p.get_or_add_pPr()
                pPr.append(OxmlElement("w:bidi"))
                jc = OxmlElement("w:jc"); jc.set(qn("w:val"),"right"); pPr.append(jc)
            lines_ = str(txt).split('\n') if '\n' in str(txt) else [str(txt)]
            for li, line_ in enumerate(lines_):
                vp = p if li == 0 else cell.add_paragraph()
                vr = vp.add_run(line_.strip())
                vr.font.size = Pt(10); vr.font.name = "Arial"; vr.font.bold = bold_
                if header: vr.font.color.rgb = RGBColor(0xFF,0xFF,0xFF)
            tc = cell._tc; tcP = tc.get_or_add_tcPr()
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'),'clear'); shd.set(qn('w:color'),'auto')
            if header:
                shd.set(qn('w:fill'), '3B5FC0' if idx==0 else '5B7FD0')
            elif idx == 0:
                shd.set(qn('w:fill'), 'E8EEFF')
            else:
                shd.set(qn('w:fill'), 'FFFFFF')
            tcP.append(shd)
            mg = OxmlElement('w:tcMar')
            for side in ['top','bottom','left','right']:
                m = OxmlElement(f'w:{side}'); m.set(qn('w:w'),'60'); m.set(qn('w:type'),'dxa'); mg.append(m)
            tcP.append(mg)

    # ── Header ──
    p_hdr = doc.add_paragraph()
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr.paragraph_format.space_before = Pt(0)
    p_hdr.paragraph_format.space_after  = Pt(6)
    if os.path.exists(LOGO_PATH):
        p_hdr.add_run().add_picture(LOGO_PATH, width=Inches(3.0))

    title_text = ("Conners' Parent Rating Scale — Clinical Report" if lang=="en"
                  else "تقرير مقياس كونرز للوالدين — التقرير السريري")
    r_t = p_hdr.add_run(f"\n{title_text}")
    r_t.font.name = "Arial"; r_t.font.size = Pt(17)
    r_t.font.bold = True; r_t.font.color.rgb = CLINIC_BLUE_RGB

    sub_text = "CPRS-R:L — Conners' Parent Rating Scale — Revised: Long Version" if lang=="en" \
               else "CPRS-R:L — مقياس كونرز للوالدين — نسخة مراجعة طويلة"
    add_para(sub_text, size=9.5, color=LOGO_BLUE_RGB,
             alignment=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)

    # Separator
    p_sep = doc.add_paragraph()
    p_sep.paragraph_format.space_before = Pt(2)
    p_sep.paragraph_format.space_after  = Pt(8)
    pPr = p_sep._p.get_or_add_pPr()
    pBdr2 = OxmlElement('w:pBdr')
    bot2  = OxmlElement('w:bottom')
    bot2.set(qn('w:val'),'single'); bot2.set(qn('w:sz'),'8')
    bot2.set(qn('w:space'),'2');    bot2.set(qn('w:color'),'A1B6F3')
    pBdr2.append(bot2); pPr.append(pBdr2)

    # Client info table
    info_tbl = make_table()
    if lang == "en":
        add_row(info_tbl, "Field", "Value", header=True)
        add_row(info_tbl, "Child", child_name)
        add_row(info_tbl, "Age", age)
        add_row(info_tbl, "Gender", gender)
        add_row(info_tbl, "Rater", rater)
        add_row(info_tbl, "Date", date.today().strftime('%B %d, %Y'))
        add_row(info_tbl, "Assessment", "CPRS-R:L (80 items, scale 0–3)")
    else:
        add_row(info_tbl, "الحقل", "البيانات", header=True)
        add_row(info_tbl, "الطفل", child_name)
        add_row(info_tbl, "السن", age)
        add_row(info_tbl, "النوع", gender)
        add_row(info_tbl, "المُقيِّم", rater)
        add_row(info_tbl, "التاريخ", date.today().strftime('%Y/%m/%d'))
        add_row(info_tbl, "المقياس", "CPRS-R:L (80 بنداً، مقياس 0–3)")
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Score summary table
    sec_title = "SUBSCALE SCORE SUMMARY" if lang=="en" else "ملخص درجات المقاييس الفرعية"
    add_section_title(sec_title)
    score_tbl = make_table()
    if lang == "en":
        add_row(score_tbl, "Subscale", "Raw | T-Score | Classification", header=True)
        for key in "ABCDEFGHIJKLMN":
            info = SUBSCALES[key]
            s    = scores[key]
            add_row(score_tbl,
                    f"{key}. {info['name_en']}",
                    f"{s['raw']}/{s['max_raw']}  |  T={s['t']}  |  {get_level_en(s['t'])}")
    else:
        add_row(score_tbl, "المقياس الفرعي", "الخام | التائي | التصنيف", header=True)
        for key in "ABCDEFGHIJKLMN":
            info = SUBSCALES[key]
            s    = scores[key]
            add_row(score_tbl,
                    f"{key}. {info['name_ar']}",
                    f"{s['raw']}/{s['max_raw']}  |  T={s['t']}  |  {get_level_ar(s['t'])}")
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Bar chart
    chart_title = "T-SCORE PROFILE CHART" if lang=="en" else "مخطط الدرجات التائية"
    add_section_title(chart_title)
    p_chart = doc.add_paragraph()
    p_chart.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_chart.paragraph_format.space_after = Pt(6)
    p_chart.add_run().add_picture(io.BytesIO(bar_chart_bytes), width=Inches(6.2))

    # Pie chart
    pie_title = "RESPONSE DISTRIBUTION" if lang=="en" else "توزيع الاستجابات"
    add_section_title(pie_title)
    p_pie = doc.add_paragraph()
    p_pie.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_pie.paragraph_format.space_after = Pt(6)
    p_pie.add_run().add_picture(io.BytesIO(pie_chart_bytes), width=Inches(4.0))

    # AI narrative report
    narrative_title = "CLINICAL NARRATIVE REPORT" if lang=="en" else "التقرير السريري التفصيلي"
    add_section_title(narrative_title)

    sec_en_pat = re.compile(r'^\d+\.\s+[A-Z][A-Z\s&/\(\):]+$')
    sec_ar_pat = re.compile(r'^[١٢٣٤٥٦٧٨٩\d]+[\.،:]\s+[\u0600-\u06FF]')
    header_words = {
        "CONNERS' PARENT RATING SCALE — CLINICAL REPORT",
        "CLINICAL SUMMARY", "REPORT HEADER",
        "تقرير مقياس كونرز للوالدين", "ملخص سريري"
    }

    in_table = False; current_table = None
    for line in report_text.split('\n'):
        ls = line.strip()
        if not ls:
            if in_table: in_table = False; current_table = None
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue

        is_section = (sec_en_pat.match(ls) or sec_ar_pat.match(ls) or
                      ls in header_words or ls.upper() in header_words)
        if is_section:
            in_table = False; current_table = None
            add_section_title(ls)
            continue

        if ls.startswith('━') or ls.startswith('═'):
            in_table = False; current_table = None
            p = doc.add_paragraph()
            pPr = p._p.get_or_add_pPr()
            pBdr = OxmlElement('w:pBdr')
            b = OxmlElement('w:bottom')
            b.set(qn('w:val'),'single'); b.set(qn('w:sz'),'4')
            b.set(qn('w:space'),'1');    b.set(qn('w:color'),'C5D3F5')
            pBdr.append(b); pPr.append(pBdr)
            continue

        if '|' in ls:
            parts = [p.strip() for p in ls.split('|') if p.strip()]
            if not parts: continue
            if all(set(p) <= set('-: ') for p in parts): continue
            skip = [("field","value"),("subscale","raw"),("المقياس","الخام"),
                    ("الحقل","البيانات"),("milestone","finding")]
            if len(parts)>=2 and (parts[0].strip('* ').lower(), parts[1].strip('* ').lower()) in skip:
                continue
            if not in_table or current_table is None:
                in_table = True; current_table = make_table()
                hdr = ("Field","Details") if lang=="en" else ("الحقل","التفاصيل")
                add_row(current_table, hdr[0], hdr[1], header=True)
            field = parts[0].strip('* ')
            value = ' | '.join(parts[1:])
            add_row(current_table, field, value)
            continue

        is_ar = any('\u0600' <= c <= '\u06ff' for c in ls)
        if ls.endswith(':') and is_ar and len(ls) < 60:
            in_table = False; current_table = None
            add_para(ls.rstrip(':'), bold=True, size=11, color=DARK_BLUE_RGB,
                     space_before=10, space_after=2, keep_next=True)
            continue

        in_table = False; current_table = None
        add_para(ls, size=10.5, space_before=0, space_after=3)

    # Footer note
    doc.add_paragraph().paragraph_format.space_after = Pt(10)
    note = ("This report is strictly confidential. Scores are based on parent/caregiver rating "
            "and should be interpreted in conjunction with clinical judgment and other assessment data. "
            "CPRS-R:L T-scores ≥65 are considered clinically significant.") if lang=="en" \
           else ("هذا التقرير سري للغاية. الدرجات مبنية على تقييم الوالدين وتُفسَّر بالتزامن مع "
                 "الحكم السريري وبيانات التقييم الأخرى. الدرجات التائية ≥65 تعتبر ذات دلالة سريرية.")
    add_para(note, size=8.5, color=LOGO_BLUE_RGB, space_before=6)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf

# ══════════════════════════════════════════════════════════════
#  EMAIL
# ══════════════════════════════════════════════════════════════
def send_email(child_name, buf_en, buf_ar, fn_en, fn_ar, scores):
    date_str = date.today().strftime('%B %d, %Y')
    elevated = [(k, scores[k]["t"]) for k in "ABCDEFGHIJKLMN" if scores[k]["t"] >= 65]
    elev_html = "".join(
        f"<tr><td style='padding:4px 0;color:#555;'>{SUBSCALES[k]['name_en']}</td>"
        f"<td><strong style='color:#D32F2F;'>T={t}</strong></td></tr>"
        for k, t in elevated
    ) or "<tr><td colspan='2' style='color:#388E3C;'>No subscales elevated ≥ 65</td></tr>"

    msg = MIMEMultipart('mixed')
    msg['From']    = GMAIL_USER
    msg['To']      = RECIPIENT_EMAIL
    msg['Subject'] = f"[Conners CPRS-R:L] {child_name} — {date_str}"

    body = f"""<html><body style="font-family:Georgia,serif;color:#1C1917;background:#F0F4FF;padding:20px;">
  <div style="max-width:560px;margin:0 auto;background:white;border:1px solid #C5D3F5;border-radius:6px;padding:28px;">
    <h2 style="font-weight:400;font-size:20px;color:#3B5FC0;margin-bottom:4px;">Conners' CPRS-R:L Report</h2>
    <p style="color:#888;font-size:11px;margin-top:0;text-transform:uppercase;letter-spacing:.08em;">
      Conners' Parent Rating Scale — Revised: Long Version</p>
    <hr style="border:none;border-top:1px solid #DDE5F8;margin:16px 0;">
    <table style="width:100%;font-size:13px;border-collapse:collapse;">
      <tr><td style="padding:5px 0;color:#555;width:40%;">Child</td><td><strong>{child_name}</strong></td></tr>
      <tr><td style="padding:5px 0;color:#555;">Date</td><td>{date_str}</td></tr>
    </table>
    <hr style="border:none;border-top:1px solid #DDE5F8;margin:16px 0;">
    <p style="font-size:12px;color:#555;font-weight:bold;margin-bottom:6px;">Elevated Subscales (T≥65)</p>
    <table style="width:100%;font-size:12px;border-collapse:collapse;">{elev_html}</table>
    <hr style="border:none;border-top:1px solid #DDE5F8;margin:16px 0;">
    <p style="font-size:12px;">Both English and Arabic reports are attached as Word documents.</p>
    <p style="font-size:10px;color:#888;font-style:italic;">Confidential — for the treating clinician only.</p>
  </div></body></html>"""

    msg.attach(MIMEText(body, 'html'))
    for buf_, fname_ in [(buf_en, fn_en), (buf_ar, fn_ar)]:
        buf_.seek(0)
        part = MIMEBase('application',
                        'vnd.openxmlformats-officedocument.wordprocessingml.document')
        part.set_payload(buf_.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=fname_)
        msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as srv:
        srv.login(GMAIL_USER, GMAIL_PASS)
        srv.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG & CSS
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Conners CPRS-R:L | مقياس كونرز",
    page_icon="🧠",
    layout="wide"
)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', 'Cairo', sans-serif;
    background-color: {LIGHT_BG};
}}
.stApp {{ background-color: {LIGHT_BG}; }}

.field-label {{
    font-size: 12.5px; font-weight: 600;
    color: {DARK_BLUE}; margin-bottom: 6px;
}}
.sec-header {{
    font-size: 14px; font-weight: 700; color: {DEEP_BLUE};
    margin: 24px 0 10px 0; padding: 10px 16px;
    background: white; border-radius: 10px;
    border-right: 4px solid {LOGO_BLUE}; border-left: 4px solid {LOGO_BLUE};
    box-shadow: 0 2px 8px rgba(59,95,192,0.08);
}}
.item-card {{
    background: white; border: 1.5px solid #DDE5F8;
    border-radius: 10px; padding: 14px 18px 8px;
    margin-bottom: 10px;
    box-shadow: 0 1px 4px rgba(59,95,192,0.06);
}}
.item-num {{
    font-size: 10.5px; font-weight: 700; color: {MID_BLUE};
    letter-spacing: .08em; margin-bottom: 4px;
}}
.item-text {{
    font-size: 14px; color: {DARK_BLUE};
    line-height: 1.5; margin-bottom: 10px;
    font-family: 'Cairo', 'Inter', sans-serif;
}}

/* ── Radio pills ── */
div[data-testid="stRadio"] > label {{ display: none; }}
div[data-testid="stRadio"] > div {{
    gap: 8px !important; flex-direction: row !important; flex-wrap: wrap !important;
}}
div[data-testid="stRadio"] > div > label {{
    background: #F0F4FF !important; border: 2px solid {LOGO_BLUE} !important;
    border-radius: 50px !important; padding: 6px 18px !important;
    font-size: 12.5px !important; color: {DEEP_BLUE} !important;
    font-family: 'Cairo','Inter',sans-serif !important;
    cursor: pointer !important; transition: all 0.15s !important;
    white-space: nowrap !important;
}}
div[data-testid="stRadio"] > div > label:has(input:checked) {{
    background: {DEEP_BLUE} !important; color: white !important;
    border-color: {DEEP_BLUE} !important;
}}

div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] {{
    background: white !important;
    border: 1.5px solid #C5D3F5 !important;
    border-radius: 8px !important;
    font-family: 'Cairo','Inter',sans-serif !important;
}}

.stButton > button {{
    background: {DEEP_BLUE} !important; color: white !important;
    border: none !important; border-radius: 10px !important;
    padding: 10px 26px !important; font-size: 14px !important;
    font-weight: 600 !important; font-family: 'Cairo','Inter',sans-serif !important;
    transition: all 0.2s !important;
    box-shadow: 0 2px 10px rgba(59,95,192,0.25) !important;
}}
.stButton > button:hover {{
    background: {MID_BLUE} !important;
    box-shadow: 0 4px 14px rgba(59,95,192,0.4) !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, {DEEP_BLUE}, {MID_BLUE}) !important;
    font-size: 16px !important; padding: 14px 40px !important;
}}

.lang-toggle {{
    display: flex; gap: 12px; justify-content: center;
    margin-bottom: 24px;
}}

div[data-testid="stDivider"] {{ margin: 16px 0; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════════════
if "lang"        not in st.session_state: st.session_state.lang = "en"
if "responses"   not in st.session_state: st.session_state.responses = {}
if "submitted"   not in st.session_state: st.session_state.submitted = False
if "report_done" not in st.session_state: st.session_state.report_done = False

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
col_logo, col_title = st.columns([1, 5])
with col_logo:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=120)
with col_title:
    st.markdown(f"""
    <div style="padding:8px 0;">
        <div style="font-size:23px;font-weight:700;color:{DEEP_BLUE};
                    font-family:'Cairo',sans-serif;line-height:1.3;">
            Conners' CPRS-R:L &nbsp;|&nbsp; مقياس كونرز للوالدين
        </div>
        <div style="font-size:12.5px;color:{MID_BLUE};margin-top:3px;">
            Conners' Parent Rating Scale — Revised: Long Version
        </div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ══════════════════════════════════════════════════════════════
#  LANGUAGE TOGGLE
# ══════════════════════════════════════════════════════════════
c1, c2, c3 = st.columns([2, 2, 4])
with c1:
    if st.button("🇬🇧 English", use_container_width=True):
        st.session_state.lang = "en"
        st.session_state.responses = {}
        st.session_state.submitted = False
        st.session_state.report_done = False
        st.rerun()
with c2:
    if st.button("🇸🇦 العربية", use_container_width=True):
        st.session_state.lang = "ar"
        st.session_state.responses = {}
        st.session_state.submitted = False
        st.session_state.report_done = False
        st.rerun()

lang = st.session_state.lang

st.markdown(f"""
<div style="text-align:center;padding:4px 0 12px;
    font-size:12px;color:{MID_BLUE};letter-spacing:.08em;">
    {'🇬🇧 Currently in English mode' if lang=='en' else '🇸🇦 النسخة العربية نشطة حالياً'}
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  RESULT DISPLAY (if already submitted)
# ══════════════════════════════════════════════════════════════
if st.session_state.report_done:
    scores    = st.session_state["scores"]
    rt_en     = st.session_state["report_en"]
    rt_ar     = st.session_state["report_ar"]
    child_name= st.session_state["child_name"]
    age       = st.session_state["child_age"]
    gender    = st.session_state["child_gender"]
    rater     = st.session_state["rater"]

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{DEEP_BLUE},{MID_BLUE});
                border-radius:12px;padding:16px 24px;margin-bottom:20px;
                color:white;font-size:15px;font-weight:600;font-family:'Cairo',sans-serif;">
        ✅ {'Report Generated Successfully' if lang=='en' else 'تم إنشاء التقرير بنجاح'} — {child_name}
    </div>""", unsafe_allow_html=True)

    # Score summary
    st.subheader("📊 T-Score Summary" if lang=="en" else "📊 ملخص الدرجات التائية")
    cols = st.columns(4)
    elevated_count = sum(1 for k in "ABCDEFGHIJKLMN" if scores[k]["t"] >= 65)
    for i, (key, label) in enumerate([
        ("ADHD Index H", "ADHD Index"),
        ("Oppositional A", "Oppositional"),
        ("Hyperactivity C", "Hyperactivity"),
        ("CGI Total K", "CGI Total"),
    ]):
        k_real = key.split()[1]
        t_val  = scores[k_real]["t"]
        col_   = cols[i % 4]
        with col_:
            st.metric(label, f"T={t_val}",
                      delta=f"{'↑ Elevated' if t_val>=65 else '✓ Normal'}",
                      delta_color="inverse" if t_val>=65 else "normal")

    # Charts
    bar_bytes = make_bar_chart(scores, "en")
    pie_bytes = make_pie_chart(st.session_state["responses"])
    tab_chart, tab_en, tab_ar = st.tabs([
        "📈 T-Score Chart",
        "🇬🇧 English Report",
        "🇸🇦 Arabic Report"
    ])
    with tab_chart:
        c1_, c2_ = st.columns([3,1])
        with c1_:
            st.image(bar_bytes, use_container_width=True)
        with c2_:
            st.image(pie_bytes, use_container_width=True)

        # Score table
        st.markdown("#### Subscale Scores")
        score_data = []
        for key in "ABCDEFGHIJKLMN":
            s = scores[key]
            score_data.append({
                "Scale": f"{key}. {SUBSCALES[key]['name_en']}",
                "Raw": f"{s['raw']}/{s['max_raw']}",
                "T-Score": s['t'],
                "Classification": get_level_en(s['t']),
                "Flag": "🔴" if s['t']>=70 else "🟠" if s['t']>=65 else "🟡" if s['t']>=60 else "🟢"
            })
        st.dataframe(score_data, use_container_width=True, hide_index=True)

    with tab_en:
        st.text_area("", value=rt_en, height=500, label_visibility="collapsed")
    with tab_ar:
        st.text_area("", value=rt_ar, height=500, label_visibility="collapsed")

    # Download buttons
    st.divider()
    fn_en = f"{child_name.replace(' ','_')}_Conners_EN.docx"
    fn_ar = f"{child_name.replace(' ','_')}_Conners_AR.docx"

    dl1, dl2, dl3, dl4 = st.columns(4)
    with dl1:
        buf_en = build_word_report(rt_en, scores, bar_bytes, pie_bytes,
                                   child_name, age, gender, rater, "en")
        st.download_button("📄 English Report (.docx)", data=buf_en,
                           file_name=fn_en, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           use_container_width=True)
    with dl2:
        buf_ar = build_word_report(rt_ar, scores, bar_bytes, pie_bytes,
                                   child_name, age, gender, rater, "ar")
        st.download_button("📄 التقرير العربي (.docx)", data=buf_ar,
                           file_name=fn_ar, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                           use_container_width=True)
    with dl3:
        if st.button("📧 Send via Email / إرسال بالبريد", use_container_width=True):
            try:
                bar_bytes2 = make_bar_chart(scores, "en")
                pie_bytes2 = make_pie_chart(st.session_state["responses"])
                buf_en2 = build_word_report(rt_en, scores, bar_bytes2, pie_bytes2,
                                            child_name, age, gender, rater, "en")
                buf_ar2 = build_word_report(rt_ar, scores, bar_bytes2, pie_bytes2,
                                            child_name, age, gender, rater, "ar")
                send_email(child_name, buf_en2, buf_ar2, fn_en, fn_ar, scores)
                st.success(f"✅ Sent to {RECIPIENT_EMAIL}")
            except Exception as e:
                st.error(f"Email error: {e}")
    with dl4:
        if st.button("↺ New Assessment / تقييم جديد", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k not in {"lang"}:
                    del st.session_state[k]
            st.session_state.responses   = {}
            st.session_state.submitted   = False
            st.session_state.report_done = False
            st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════
#  INTAKE FORM
# ══════════════════════════════════════════════════════════════
if lang == "en":
    st.markdown(f'<div class="sec-header">👤 Child Information</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="field-label">Child\'s Full Name</div>', unsafe_allow_html=True)
        child_name = st.text_input("", key="child_name_inp", placeholder="First and last name",
                                   label_visibility="collapsed")
        st.markdown('<div class="field-label">Age</div>', unsafe_allow_html=True)
        child_age  = st.text_input("", key="child_age_inp",  placeholder="e.g. 8",
                                   label_visibility="collapsed")
    with c2:
        st.markdown('<div class="field-label">Gender</div>', unsafe_allow_html=True)
        child_gender = st.radio("", ["Male","Female"], key="child_gender_inp",
                                horizontal=True, label_visibility="collapsed")
        st.markdown('<div class="field-label">School Grade</div>', unsafe_allow_html=True)
        child_grade  = st.text_input("", key="child_grade_inp", placeholder="e.g. Grade 3",
                                     label_visibility="collapsed")
    with c3:
        st.markdown('<div class="field-label">Rater\'s Name (Parent / Caregiver)</div>', unsafe_allow_html=True)
        rater = st.text_input("", key="rater_inp", placeholder="Name",
                              label_visibility="collapsed")
        st.markdown('<div class="field-label">Relationship to Child</div>', unsafe_allow_html=True)
        relationship = st.text_input("", key="rel_inp", placeholder="e.g. Mother",
                                     label_visibility="collapsed")

    st.markdown(f"""
    <div style="background:#EFF3FF;border-radius:10px;padding:14px 18px;margin:16px 0;
                font-size:13px;color:{DARK_BLUE};border-left:4px solid {DEEP_BLUE};">
        <strong>Instructions:</strong> Below are common problems that children have.
        Please rate each item based on your child's behaviour <strong>in the last month</strong>.
        For each item, choose:<br>
        <strong>0</strong> = Not at all &nbsp;|&nbsp;
        <strong>1</strong> = Just a little &nbsp;|&nbsp;
        <strong>2</strong> = Pretty much &nbsp;|&nbsp;
        <strong>3</strong> = Very much
    </div>""", unsafe_allow_html=True)

    SCALE_OPTS  = ["0 — Not at all", "1 — Just a little", "2 — Pretty much", "3 — Very much"]
    ITEMS       = ITEMS_EN

else:  # Arabic
    st.markdown(f'<div class="sec-header" style="direction:rtl;">👤 بيانات الطفل</div>',
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="field-label" style="direction:rtl;text-align:right;">اسم الطفل كاملاً</div>', unsafe_allow_html=True)
        child_name = st.text_input("", key="child_name_inp", placeholder="الاسم الأول والأخير",
                                   label_visibility="collapsed")
        st.markdown('<div class="field-label" style="direction:rtl;text-align:right;">السن</div>', unsafe_allow_html=True)
        child_age  = st.text_input("", key="child_age_inp",  placeholder="مثال: 8",
                                   label_visibility="collapsed")
    with c2:
        st.markdown('<div class="field-label" style="direction:rtl;text-align:right;">النوع</div>', unsafe_allow_html=True)
        child_gender = st.radio("", ["ذكر","أنثى"], key="child_gender_inp",
                                horizontal=True, label_visibility="collapsed")
        st.markdown('<div class="field-label" style="direction:rtl;text-align:right;">الصف الدراسي</div>', unsafe_allow_html=True)
        child_grade  = st.text_input("", key="child_grade_inp", placeholder="مثال: الصف الثالث",
                                     label_visibility="collapsed")
    with c3:
        st.markdown('<div class="field-label" style="direction:rtl;text-align:right;">اسم المُقيِّم (ولي الأمر)</div>', unsafe_allow_html=True)
        rater = st.text_input("", key="rater_inp", placeholder="الاسم",
                              label_visibility="collapsed")
        st.markdown('<div class="field-label" style="direction:rtl;text-align:right;">صلة القرابة بالطفل</div>', unsafe_allow_html=True)
        relationship = st.text_input("", key="rel_inp", placeholder="مثال: الأم",
                                     label_visibility="collapsed")

    st.markdown(f"""
    <div style="background:#EFF3FF;border-radius:10px;padding:14px 18px;margin:16px 0;
                font-size:13px;color:{DARK_BLUE};border-right:4px solid {DEEP_BLUE};
                direction:rtl;text-align:right;">
        <strong>التعليمات:</strong> فيما يلي قائمة بالمشكلات الشائعة عند الأطفال.
        يرجى تقييم كل بند بناءً على سلوك طفلك <strong>خلال الشهر الماضي</strong>.
        اختر لكل بند:<br>
        <strong>0</strong> = أبداً / نادراً &nbsp;|&nbsp;
        <strong>1</strong> = أحياناً بدرجة قليلة &nbsp;|&nbsp;
        <strong>2</strong> = إلى حد ما / كثيراً &nbsp;|&nbsp;
        <strong>3</strong> = صحيح جداً / كثيراً جداً
    </div>""", unsafe_allow_html=True)

    SCALE_OPTS  = ["0 — أبداً", "1 — أحياناً", "2 — إلى حد ما", "3 — كثيراً جداً"]
    ITEMS       = ITEMS_AR

# ══════════════════════════════════════════════════════════════
#  ITEM RENDERING  (80 items)
# ══════════════════════════════════════════════════════════════
responses = st.session_state.responses
all_answered = True

for idx, item_text in enumerate(ITEMS):
    item_num = idx + 1
    direction = 'rtl' if lang=='ar' else 'ltr'
    align     = 'right' if lang=='ar' else 'left'
    label_prefix = ("بند" if lang=="ar" else "Item")

    st.markdown(f"""
    <div class="item-card" style="direction:{direction};">
        <div class="item-num" style="text-align:{align};">{label_prefix} {item_num} / 80</div>
        <div class="item-text" style="text-align:{align};">{item_text}</div>
    </div>""", unsafe_allow_html=True)

    saved = responses.get(item_num)
    idx_saved = None
    if saved is not None:
        idx_saved = saved

    choice = st.radio(
        f"item_{item_num}",
        SCALE_OPTS,
        index=idx_saved,
        key=f"resp_{item_num}",
        horizontal=True,
        label_visibility="collapsed"
    )
    if choice is None:
        all_answered = False
    else:
        val = int(choice[0])
        responses[item_num] = val
        st.session_state.responses[item_num] = val

# ══════════════════════════════════════════════════════════════
#  PROGRESS & SUBMIT
# ══════════════════════════════════════════════════════════════
answered_count = len([v for v in responses.values() if v is not None])
pct = int((answered_count / 80) * 100)

prog_text = f"{answered_count} of 80 answered" if lang=="en" else f"{answered_count} من 80 بنداً"
st.markdown(f"""
<div style="text-align:center;font-size:12px;color:{MID_BLUE};
            letter-spacing:.06em;margin-top:16px;">{prog_text}</div>
<div style="background:#DDE5F8;border-radius:3px;height:4px;margin:8px 0 4px 0;">
    <div style="width:{pct}%;height:4px;border-radius:3px;
                background:linear-gradient(90deg,{DEEP_BLUE},{MID_BLUE});"></div>
</div>""", unsafe_allow_html=True)

if not all_answered and answered_count > 0:
    warn = "⚠ Please answer all 80 items before submitting." if lang=="en" \
           else "⚠ يرجى الإجابة على جميع البنود الـ 80 قبل الإرسال."
    st.warning(warn)

st.markdown("<br>", unsafe_allow_html=True)
btn_label = "✦ Generate Report" if lang=="en" else "✦ توليد التقرير"
col_btn, _ = st.columns([2,3])
with col_btn:
    submit = st.button(btn_label, type="primary", use_container_width=True,
                       disabled=(answered_count < 80))

if submit and answered_count == 80:
    child_name_v  = child_name  or ("Child" if lang=="en" else "الطفل")
    child_age_v   = child_age   or "—"
    child_grade_v = child_grade or "—"
    rater_v       = rater       or ("Parent" if lang=="en" else "ولي الأمر")
    gender_v      = child_gender

    with st.spinner("⏳ Scoring and generating reports..." if lang=="en"
                    else "⏳ جاري الحساب وإنشاء التقارير..."):
        scores    = compute_scores(st.session_state.responses)
        report_en = generate_report_en(child_name_v, child_age_v, gender_v, rater_v, scores)
        report_ar = generate_report_ar(child_name_v, child_age_v, gender_v, rater_v, scores)

        st.session_state["scores"]      = scores
        st.session_state["report_en"]   = report_en
        st.session_state["report_ar"]   = report_ar
        st.session_state["child_name"]  = child_name_v
        st.session_state["child_age"]   = child_age_v
        st.session_state["child_gender"]= gender_v
        st.session_state["rater"]       = rater_v
        st.session_state.report_done    = True
        st.rerun()

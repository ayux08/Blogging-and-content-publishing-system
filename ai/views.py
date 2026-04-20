import json
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def get_session_context(request):
    return {
        'user_id': request.session.get('user_id'),
        'user_name': request.session.get('user_name', 'Guest'),
        'user_role': request.session.get('user_role', 'reader'),
    }

# AI Dashboard
def index(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "ai", "page": "index"})
    return render(request, "ai/index.html", ctx)

# AI Summarize page
def summarize(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "ai", "page": "summarize"})
    return render(request, "ai/summarize.html", ctx)

# AI Translate page
def translate(request):
    ctx = get_session_context(request)
    ctx.update({"zone": "ai", "page": "translate"})
    return render(request, "ai/translate.html", ctx)

# ═══════════════════════════════════════════════════════════════
# Word-to-word translation dictionaries
# ═══════════════════════════════════════════════════════════════

DICT_HINDI = {
    # Common words
    'the': '', 'a': 'एक', 'an': 'एक', 'is': 'है', 'are': 'हैं', 'was': 'था', 'were': 'थे',
    'has': 'है', 'have': 'है', 'had': 'था', 'will': 'होगा', 'would': 'होगा', 'can': 'कर सकता',
    'could': 'कर सकता', 'shall': 'होगा', 'should': 'चाहिए', 'may': 'सकता', 'might': 'शायद',
    'must': 'जरूर', 'do': 'करना', 'does': 'करता', 'did': 'किया', 'not': 'नहीं',
    'and': 'और', 'or': 'या', 'but': 'लेकिन', 'if': 'अगर', 'then': 'तो', 'else': 'अन्यथा',
    'when': 'जब', 'where': 'कहाँ', 'how': 'कैसे', 'what': 'क्या', 'which': 'कौन', 'who': 'कौन',
    'this': 'यह', 'that': 'वह', 'these': 'ये', 'those': 'वे', 'here': 'यहाँ', 'there': 'वहाँ',
    'in': 'में', 'on': 'पर', 'at': 'पर', 'to': 'को', 'from': 'से', 'with': 'के साथ',
    'for': 'के लिए', 'of': 'का', 'by': 'द्वारा', 'about': 'के बारे में', 'into': 'में',
    'through': 'के माध्यम से', 'during': 'के दौरान', 'before': 'पहले', 'after': 'बाद',
    'above': 'ऊपर', 'below': 'नीचे', 'between': 'बीच', 'under': 'के अंतर्गत',
    'i': 'मैं', 'you': 'आप', 'he': 'वह', 'she': 'वह', 'it': 'यह', 'we': 'हम', 'they': 'वे',
    'my': 'मेरा', 'your': 'आपका', 'his': 'उसका', 'her': 'उसकी', 'its': 'इसका', 'our': 'हमारा', 'their': 'उनका',
    'me': 'मुझे', 'him': 'उसे', 'us': 'हमें', 'them': 'उनको',
    'all': 'सभी', 'each': 'प्रत्येक', 'every': 'हर', 'both': 'दोनों', 'few': 'कुछ', 'more': 'अधिक',
    'most': 'सबसे', 'other': 'अन्य', 'some': 'कुछ', 'any': 'कोई', 'no': 'नहीं', 'many': 'बहुत',
    'much': 'बहुत', 'very': 'बहुत', 'also': 'भी', 'just': 'बस', 'only': 'केवल', 'still': 'अभी भी',
    'now': 'अब', 'new': 'नया', 'old': 'पुराना', 'first': 'पहला', 'second': 'दूसरा', 'third': 'तीसरा',
    'last': 'आखिरी', 'long': 'लंबा', 'great': 'महान', 'little': 'छोटा', 'big': 'बड़ा',
    'good': 'अच्छा', 'bad': 'बुरा', 'best': 'सबसे अच्छा', 'better': 'बेहतर', 'well': 'अच्छी तरह',
    'high': 'ऊँचा', 'low': 'कम', 'right': 'सही', 'left': 'बाएँ', 'own': 'अपना',
    'same': 'समान', 'different': 'अलग', 'important': 'महत्वपूर्ण', 'large': 'बड़ा', 'small': 'छोटा',
    'world': 'दुनिया', 'life': 'जीवन', 'time': 'समय', 'day': 'दिन', 'year': 'साल', 'way': 'तरीका',
    'people': 'लोग', 'man': 'आदमी', 'woman': 'महिला', 'child': 'बच्चा', 'children': 'बच्चे',
    'work': 'काम', 'thing': 'चीज़', 'things': 'चीज़ें', 'place': 'जगह', 'system': 'प्रणाली',
    'part': 'भाग', 'number': 'संख्या', 'water': 'पानी', 'hand': 'हाथ', 'home': 'घर',
    'make': 'बनाना', 'made': 'बनाया', 'like': 'जैसा', 'get': 'पाना', 'give': 'देना',
    'go': 'जाना', 'come': 'आना', 'take': 'लेना', 'know': 'जानना', 'think': 'सोचना',
    'say': 'कहना', 'said': 'कहा', 'see': 'देखना', 'use': 'उपयोग', 'find': 'खोजना',
    'tell': 'बताना', 'ask': 'पूछना', 'need': 'जरूरत', 'try': 'कोशिश', 'call': 'बुलाना',
    'keep': 'रखना', 'let': 'देना', 'begin': 'शुरू', 'show': 'दिखाना', 'help': 'मदद',
    'start': 'शुरू', 'run': 'चलाना', 'move': 'चलना', 'play': 'खेलना', 'read': 'पढ़ना',
    'write': 'लिखना', 'learn': 'सीखना', 'grow': 'बढ़ना', 'open': 'खोलना', 'close': 'बंद',
    'stop': 'रुकना', 'change': 'बदलना', 'follow': 'अनुसरण', 'lead': 'नेतृत्व', 'create': 'बनाना',
    'build': 'निर्माण', 'set': 'सेट', 'include': 'शामिल', 'continue': 'जारी रखना',
    'turn': 'बदलना', 'provide': 'प्रदान', 'become': 'बनना', 'remain': 'रहना',
    'look': 'देखना', 'bring': 'लाना', 'feel': 'महसूस', 'seem': 'लगना', 'leave': 'छोड़ना',
    'put': 'रखना', 'mean': 'मतलब', 'pay': 'भुगतान', 'believe': 'विश्वास',
    'hold': 'पकड़ना', 'stand': 'खड़ा', 'happen': 'होना', 'carry': 'ले जाना',
    'understand': 'समझना', 'watch': 'देखना', 'develop': 'विकसित', 'produce': 'उत्पादन',
    'one': 'एक', 'two': 'दो', 'three': 'तीन', 'four': 'चार', 'five': 'पाँच',
    'six': 'छह', 'seven': 'सात', 'eight': 'आठ', 'nine': 'नौ', 'ten': 'दस',
    'technology': 'प्रौद्योगिकी', 'software': 'सॉफ्टवेयर', 'computer': 'कंप्यूटर',
    'development': 'विकास', 'developer': 'डेवलपर', 'developers': 'डेवलपर्स',
    'artificial': 'कृत्रिम', 'intelligence': 'बुद्धिमत्ता', 'tools': 'उपकरण', 'tool': 'उपकरण',
    'code': 'कोड', 'coding': 'कोडिंग', 'testing': 'परीक्षण', 'test': 'परीक्षा',
    'automated': 'स्वचालित', 'automation': 'स्वचालन', 'platform': 'मंच', 'platforms': 'मंचों',
    'data': 'डेटा', 'digital': 'डिजिटल', 'online': 'ऑनलाइन', 'web': 'वेब',
    'blog': 'ब्लॉग', 'article': 'लेख', 'post': 'पोस्ट', 'content': 'सामग्री',
    'writing': 'लेखन', 'writer': 'लेखक', 'author': 'लेखक', 'reader': 'पाठक',
    'review': 'समीक्षा', 'top': 'शीर्ष', 'best': 'सर्वश्रेष्ठ',
    'quality': 'गुणवत्ता', 'assurance': 'आश्वासन', 'reliable': 'विश्वसनीय',
    'faster': 'तेज', 'fast': 'तेज', 'slow': 'धीमा', 'quick': 'जल्दी',
    'comprehensive': 'व्यापक', 'complete': 'पूर्ण', 'automatic': 'स्वचालित',
    'automatically': 'स्वचालित रूप से', 'documentation': 'दस्तावेज़ीकरण',
    'generate': 'उत्पन्न', 'generation': 'उत्पादन', 'innovation': 'नवाचार', 'innovations': 'नवाचार',
    'productivity': 'उत्पादकता', 'industry': 'उद्योग', 'business': 'व्यापार',
    'company': 'कंपनी', 'market': 'बाजार', 'power': 'शक्ति', 'powerful': 'शक्तिशाली',
    'feature': 'सुविधा', 'features': 'सुविधाएं', 'design': 'डिज़ाइन', 'user': 'उपयोगकर्ता',
    'experience': 'अनुभव', 'performance': 'प्रदर्शन', 'result': 'परिणाम', 'results': 'परिणाम',
    'process': 'प्रक्रिया', 'support': 'सहायता', 'service': 'सेवा',
    'significantly': 'महत्वपूर्ण रूप से', 'essential': 'आवश्यक',
    'advanced': 'उन्नत', 'intelligent': 'बुद्धिमान', 'modern': 'आधुनिक',
    'transformed': 'बदल दिया', 'revolutionized': 'क्रांति ला दी',
    'boosted': 'बढ़ाया', 'reduced': 'कम किया', 'accelerated': 'गति दी',
    'maintain': 'बनाए रखना', 'completion': 'पूर्णता', 'suggestion': 'सुझाव', 'suggestions': 'सुझाव',
    'continues': 'जारी', 'delivery': 'वितरण', 'timelines': 'समय-सीमा', 'timeline': 'समय-सीमा',
    'across': 'भर में', 'bugs': 'बग', 'bug': 'बग', 'error': 'त्रुटि', 'errors': 'त्रुटियां',
    'api': 'एपीआई', 'docs': 'दस्तावेज़', 'toolkit': 'टूलकिट',
    'every': 'हर', 'way': 'तरीका',
}

DICT_TAMIL = {
    'the': '', 'a': 'ஒரு', 'an': 'ஒரு', 'is': 'ஆகும்', 'are': 'ஆகும்', 'was': 'இருந்தது', 'were': 'இருந்தன',
    'has': 'உள்ளது', 'have': 'உள்ளது', 'had': 'இருந்தது', 'will': 'வேண்டும்', 'can': 'முடியும்',
    'and': 'மற்றும்', 'or': 'அல்லது', 'but': 'ஆனால்', 'if': 'என்றால்', 'then': 'பின்',
    'not': 'இல்லை', 'in': 'இல்', 'on': 'மீது', 'at': 'இல்', 'to': 'க்கு', 'from': 'இருந்து',
    'with': 'உடன்', 'for': 'க்காக', 'of': 'இன்', 'by': 'மூலம்', 'about': 'பற்றி',
    'this': 'இது', 'that': 'அது', 'these': 'இவை', 'those': 'அவை',
    'i': 'நான்', 'you': 'நீங்கள்', 'he': 'அவன்', 'she': 'அவள்', 'it': 'இது', 'we': 'நாங்கள்', 'they': 'அவர்கள்',
    'all': 'அனைத்து', 'every': 'ஒவ்வொரு', 'many': 'பல', 'more': 'அதிகம்', 'most': 'மிகவும்',
    'new': 'புதிய', 'good': 'நல்ல', 'best': 'சிறந்த', 'first': 'முதல்', 'second': 'இரண்டாவது', 'third': 'மூன்றாவது',
    'now': 'இப்போது', 'also': 'மேலும்', 'very': 'மிகவும்', 'only': 'மட்டுமே',
    'artificial': 'செயற்கை', 'intelligence': 'நுண்ணறிவு', 'technology': 'தொழில்நுட்பம்',
    'software': 'மென்பொருள்', 'developer': 'டெவலப்பர்', 'developers': 'டெவலப்பர்கள்',
    'tools': 'கருவிகள்', 'tool': 'கருவி', 'code': 'குறியீடு', 'coding': 'குறியீட்டு',
    'testing': 'சோதனை', 'automated': 'தானியங்கி', 'platform': 'தளம்',
    'data': 'தரவு', 'digital': 'டிஜிட்டல்', 'blog': 'வலைப்பதிவு',
    'writing': 'எழுதுதல்', 'writer': 'எழுத்தாளர்', 'reader': 'வாசகர்',
    'top': 'சிறந்த', 'quality': 'தரம்', 'fast': 'வேகம்', 'faster': 'வேகமான',
    'world': 'உலகம்', 'time': 'நேரம்', 'work': 'வேலை', 'people': 'மக்கள்',
    'development': 'மேம்பாடு', 'modern': 'நவீன', 'advanced': 'மேம்பட்ட',
    'essential': 'அத்தியாவசிய', 'industry': 'தொழில்',
    'transformed': 'மாற்றியது', 'revolutionized': 'புரட்சி செய்தது',
    'significantly': 'கணிசமாக', 'productivity': 'உற்பத்தித்திறன்',
    'comprehensive': 'விரிவான', 'documentation': 'ஆவணமாக்கல்',
    'generate': 'உருவாக்கு', 'automatically': 'தானாக',
    'innovations': 'கண்டுபிடிப்புகள்', 'innovation': 'கண்டுபிடிப்பு',
    'continues': 'தொடர்கிறது', 'suggestions': 'பரிந்துரைகள்',
    'reduced': 'குறைத்தது', 'boosted': 'அதிகரித்தது', 'accelerated': 'துரிதப்படுத்தியது',
    'delivery': 'வழங்குதல்', 'bugs': 'பிழைகள்', 'reliable': 'நம்பகமான',
    'across': 'முழுவதும்', 'maintain': 'பராமரிக்க',
}

DICT_TELUGU = {
    'the': '', 'a': 'ఒక', 'an': 'ఒక', 'is': 'ఉంది', 'are': 'ఉన్నాయి', 'was': 'ఉంది', 'were': 'ఉన్నాయి',
    'has': 'ఉంది', 'have': 'ఉన్నాయి', 'and': 'మరియు', 'or': 'లేదా', 'but': 'కానీ',
    'not': 'కాదు', 'in': 'లో', 'on': 'పై', 'to': 'కి', 'from': 'నుండి', 'with': 'తో',
    'for': 'కోసం', 'of': 'యొక్క', 'by': 'ద్వారా', 'about': 'గురించి',
    'this': 'ఈ', 'that': 'ఆ', 'these': 'ఈ', 'those': 'ఆ',
    'i': 'నేను', 'you': 'మీరు', 'he': 'అతను', 'she': 'ఆమె', 'it': 'ఇది', 'we': 'మేము', 'they': 'వారు',
    'all': 'అన్ని', 'every': 'ప్రతి', 'many': 'చాలా', 'more': 'ఎక్కువ', 'most': 'అత్యధిక',
    'new': 'కొత్త', 'good': 'మంచి', 'best': 'ఉత్తమ', 'first': 'మొదటి', 'second': 'రెండవ', 'third': 'మూడవ',
    'now': 'ఇప్పుడు', 'also': 'కూడా', 'very': 'చాలా', 'only': 'మాత్రమే',
    'artificial': 'కృత్రిమ', 'intelligence': 'మేధస్సు', 'technology': 'సాంకేతిక పరిజ్ఞానం',
    'software': 'సాఫ్ట్‌వేర్', 'developer': 'డెవలపర్', 'developers': 'డెవలపర్లు',
    'tools': 'సాధనాలు', 'tool': 'సాధనం', 'code': 'కోడ్', 'testing': 'పరీక్ష',
    'automated': 'స్వయంచాలక', 'development': 'అభివృద్ధి', 'blog': 'బ్లాగ్',
    'writing': 'రాయడం', 'top': 'అగ్ర', 'quality': 'నాణ్యత', 'world': 'ప్రపంచం',
    'time': 'సమయం', 'work': 'పని', 'people': 'ప్రజలు', 'modern': 'ఆధునిక',
    'essential': 'అవసరమైన', 'industry': 'పరిశ్రమ',
    'transformed': 'మార్చింది', 'revolutionized': 'విప్లవం చేసింది',
    'significantly': 'గణనీయంగా', 'productivity': 'ఉత్పాదకత',
    'innovations': 'ఆవిష్కరణలు', 'comprehensive': 'సమగ్ర',
    'documentation': 'డాక్యుమెంటేషన్', 'automatically': 'స్వయంచాలకంగా',
    'reduced': 'తగ్గించింది', 'boosted': 'పెంచింది', 'accelerated': 'వేగవంతం చేసింది',
    'delivery': 'డెలివరీ', 'bugs': 'బగ్‌లు', 'reliable': 'నమ్మదగిన',
    'across': 'అంతటా', 'maintain': 'నిర్వహించడం',
}

DICT_MARATHI = {
    'the': '', 'a': 'एक', 'an': 'एक', 'is': 'आहे', 'are': 'आहेत', 'was': 'होता', 'were': 'होते',
    'has': 'आहे', 'have': 'आहे', 'and': 'आणि', 'or': 'किंवा', 'but': 'पण',
    'not': 'नाही', 'in': 'मध्ये', 'on': 'वर', 'to': 'ला', 'from': 'पासून', 'with': 'सोबत',
    'for': 'साठी', 'of': 'चा', 'by': 'द्वारे', 'about': 'बद्दल',
    'this': 'हे', 'that': 'ते', 'these': 'हे', 'those': 'ते',
    'i': 'मी', 'you': 'तुम्ही', 'he': 'तो', 'she': 'ती', 'it': 'हे', 'we': 'आम्ही', 'they': 'ते',
    'all': 'सर्व', 'every': 'प्रत्येक', 'many': 'अनेक', 'more': 'अधिक', 'most': 'सर्वात',
    'new': 'नवीन', 'good': 'चांगला', 'best': 'सर्वोत्तम', 'first': 'पहिला', 'second': 'दुसरा', 'third': 'तिसरा',
    'now': 'आता', 'also': 'सुद्धा', 'very': 'खूप', 'only': 'फक्त',
    'artificial': 'कृत्रिम', 'intelligence': 'बुद्धिमत्ता', 'technology': 'तंत्रज्ञान',
    'software': 'सॉफ्टवेअर', 'developer': 'विकासक', 'developers': 'विकासक',
    'tools': 'साधने', 'tool': 'साधन', 'code': 'कोड', 'testing': 'चाचणी',
    'automated': 'स्वयंचलित', 'development': 'विकास', 'blog': 'ब्लॉग',
    'writing': 'लेखन', 'top': 'सर्वोच्च', 'quality': 'गुणवत्ता', 'world': 'जग',
    'time': 'वेळ', 'work': 'काम', 'people': 'लोक', 'modern': 'आधुनिक',
    'essential': 'आवश्यक', 'industry': 'उद्योग',
    'transformed': 'बदलले', 'revolutionized': 'क्रांती केली',
    'significantly': 'लक्षणीय', 'productivity': 'उत्पादकता',
    'innovations': 'नवकल्पना', 'comprehensive': 'सर्वसमावेशक',
    'documentation': 'दस्तऐवजीकरण', 'automatically': 'आपोआप',
    'reduced': 'कमी केले', 'boosted': 'वाढवले', 'accelerated': 'गती वाढवली',
    'delivery': 'वितरण', 'bugs': 'बग', 'reliable': 'विश्वसनीय',
    'across': 'संपूर्ण', 'maintain': 'देखभाल करणे',
}

LANG_DICTS = {
    'Hindi': DICT_HINDI,
    'Tamil': DICT_TAMIL,
    'Telugu': DICT_TELUGU,
    'Marathi': DICT_MARATHI,
}

LANG_LABELS = {
    'Hindi': 'हिंदी अनुवाद',
    'Tamil': 'தமிழ் மொழிபெயர்ப்பு',
    'Telugu': 'తెలుగు అనువాదం',
    'Marathi': 'मराठी अनुवाद',
}

def word_by_word_translate(content, target_lang):
    """Translate content word-by-word using dictionary lookup.
       Words not found in dictionary are kept as-is (transliterated)."""
    dictionary = LANG_DICTS.get(target_lang, {})
    if not dictionary:
        return content

    # Split into words while preserving punctuation and whitespace
    tokens = re.findall(r"[\w']+|[^\w\s]|\s+", content)
    translated = []
    for token in tokens:
        lower = token.lower().strip()
        if lower in dictionary:
            tr = dictionary[lower]
            if tr:  # skip empty translations (like 'the')
                translated.append(tr)
        elif token.strip():
            translated.append(token)  # keep original (names, numbers, etc.)
        else:
            translated.append(token)  # keep whitespace
    return ' '.join(t for t in translated if t.strip() or t == ' ')


# ─── AJAX API: Summarize ─────────────────────────
@csrf_exempt
def api_summarize(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
        content = data.get("content", "").strip()
        length = data.get("length", "short")
        lang = data.get("lang", "English")

        if not content:
            return JsonResponse({"error": "No content provided"}, status=400)

        # Split the actual blog content into sentences
        sentences = re.split(r'(?<=[.!?])\s+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

        if length == "short":
            picked = sentences[:3]
        elif length == "medium":
            picked = sentences[:6]
        else:
            # Detailed: bullet-point key sentences
            picked = sentences[:8]

        if length == "detailed":
            summary = "\n".join(f"• {s}" for s in picked)
        else:
            summary = " ".join(picked)

        # If non-English language requested, translate the summary word-by-word
        if lang != "English" and lang in LANG_DICTS:
            summary = word_by_word_translate(summary, lang)

        return JsonResponse({"summary": summary, "lang": lang})
    return JsonResponse({"error": "POST required"}, status=405)

# ─── AJAX API: Translate (word-by-word) ───────────
@csrf_exempt
def api_translate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
        content = data.get("content", "").strip()
        target_lang = data.get("lang", "Hindi")

        if not content:
            return JsonResponse({"error": "No content provided"}, status=400)

        label = LANG_LABELS.get(target_lang, "Translation")

        # Word-by-word translation of the ENTIRE blog content
        translation = word_by_word_translate(content, target_lang)

        return JsonResponse({
            "translation": translation,
            "label": label,
            "lang": target_lang,
        })
    return JsonResponse({"error": "POST required"}, status=405)

"""
Indonesian Culinary NLP Parsing Engine (v2 Enhanced)
Specialized Information Retrieval parser for Indonesian recipe ingredients:
- Normalizes Indonesian fractions, culinary measurement units, and attached units
- Resolves word reduplications and strips preparation verbs and cutting styles
- Filters Cookpad conversational chatter, section headers, and non-food utensils
- Strips decorative emojis and stray unbalanced punctuation
- Maps colloquial synonyms and regional aliases to canonical terms
- Classifies functional pantry staples adaptively
- Extracts core ingredients and composite IR tokens for retrieval
"""

import re
from typing import List, Dict, Set, Tuple, Any, Optional


class IndonesianIngredientParser:
    """
    Parser bahan makanan Indonesia v2 khusus Sistem Temu Kembali Informasi:
    - Menghapus angka, pecahan takaran, dan pengubah ukuran fisik
    - Menghilangkan catatan subjektif/percakapan Cookpad (chatter)
    - Menyaring peralatan dan kemasan non-pangan
    - Mengabaikan baris penanda struktur resep (section headers)
    - Menghapus kata kerja/kondisi persiapan tanpa memotong bumbu majemuk
    - Menormalisasi sinonim ke bentuk kanonik dengan kamus terproteksi
    - Mengklasifikasikan bahan pokok dapur (pantry staples) adaptif
    - Membangun token indeks komposit untuk mesin temu kembali
    """

    # -- 1. Bahan Pokok Dapur (Pantry Staples) ---------------------------------
    PANTRY_STAPLES = frozenset({
        "air", "garam", "gula pasir", "gula", "minyak goreng", "minyak",
        "kaldu bubuk", "merica", "lada", "penyedap rasa", "msg", "micin"
    })

    # -- 2. Peralatan & Kemasan Non-Pangan -------------------------------------
    NON_FOOD_TERMS = frozenset({
        "tusuk sate", "tusukan sate", "tusuk gigi", "tusukan gigi", "lidi",
        "plastik", "kertas roti", "kertas minyak", "karet gelang", "tali",
        "daun pisang pembungkus", "alumunium foil"
    })

    # -- 3. Baris Header Seksi Resep -------------------------------------------
    RE_SECTION_HEADER = re.compile(
        r'^(?:bahan|bumbu|seasoning|pelengkap|topping|isian|olesan|marinasi|kuah|sambal|untuk|saos|saus)\b.*:|^[•\-\*#]+\s*(?:bahan|bumbu|seasoning|pelengkap|topping|isian|olesan|marinasi|kuah|sambal)',
        re.IGNORECASE
    )

    # -- 4. Catatan Percakapan Penulis Cookpad (Chatter & Notes) ---------------
    RE_CHATTER = re.compile(
        r'\b(?:resep asli|resep aslinya|kalo resep|di resep|resepnya|resep)\b.*'
        r'|\b(?:boleh skip|bisa diskip|bisa skip|skip|opsional|optional|tidak wajib|sesuai selera|selera)\b.*'
        r'|\b(?:saya pakai|aku pakai|aku pake|saya pake|tambahan sy|tambahan saya|stok lama)\b.*'
        r'|\b(?:tidak pakai|nggak pakai|gak pake|tidak ada|ga ada)\b.*',
        re.IGNORECASE
    )

    # -- 5. Klausa Tujuan Penggunaan (Purpose Clauses) --------------------------
    RE_PURPOSE = re.compile(
        r'\b(?:untuk|utk|buat)\s+(?:menumis|menggoreng|merebus|mengukus|membakar|memanggang|taburan|olesan|marinasi|kuah|sambal|sate|cocolan|pelengkap|hiasan|garnis|isian)\b'
        r'|\b(?:untuk|utk|buat)\b.*$',
        re.IGNORECASE
    )

    # -- 6. Pengubah Ukuran Fisik ----------------------------------------------
    RE_SIZES = re.compile(
        r'\b(?:uk(?:uran)?\.?\s*(?:besar|sedang|kecil|jumbo|mini)?)\b'
        r'|\b(?:besar|sedang|kecil|jumbo|mini)\b',
        re.IGNORECASE
    )

    # -- 7. Angka, Pecahan, Rentang Takaran ------------------------------------
    RE_FRACTIONS = re.compile(r'[½¼¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]')
    RE_NUMBERS = re.compile(
        r'\b\d+[\.,/]?\d*\s*[-\u2013\u2014]\s*\d+[\.,/]?\d*\b'
        r'|\b\d+\s*/\s*\d+\b'
        r'|\b\d+[\.,]\d+\b'
        r'|\b\d+\b'
    )

    # -- 8. Satuan Takaran Kuliner ---------------------------------------------
    CULINARY_UNITS = [
        "sendok makan", "sendok teh", "sendok", "sdm", "sdt", "sdk",
        "kilogram", "gram", "ons", "kg", "gr", "g",
        "mililiter", "liter", "ml", "cc", "l",
        "siung", "butir", "btr", "buah", "bh", "biji",
        "batang", "btg", "lembar", "lbr", "helai", "tangkai",
        "ruas", "jari", "cm", "telunjuk",
        "bungkus", "bks", "sachet", "sct", "pak", "papan",
        "potong", "ptg", "iris",
        "ekor", "ikat", "genggam", "segenggam", "jumput", "sejumput",
        "gelas", "cangkir", "mangkok", "mangkuk", "piring", "kaleng", "botol",
        "tetes",
        "secukupnya", "sesuai selera", "optional", "opsional",
        "kurang lebih", "kira-kira", "sedikit",
        "setengah", "seperempat", "sepertiga",
    ]

    # -- 9. Kata Kerja & Kondisi Persiapan (Bumbu Kacang & Bumbu Bebas Dihapus) --
    PREPARATION_WORDS = [
        "potong dadu", "potong korek api", "potong kecil", "potong-potong", "potong", "dipotong", "potongan",
        "iris tipis", "iris serong", "iris halus", "iris kotak", "iris-iris", "iris", "diiris", "irisan",
        "cincang halus", "cincang kasar", "cincang", "dicincang",
        "geprek", "memarkan", "dimemarkan", "dihaluskan", "haluskan", "halus", "kasar", "ulek", "blender", "giling",
        "belah dua", "belah 2", "belah 4", "belah 8", "belah", "dibelah",
        "sobek-sobek", "sobek", "disobek",
        "ambil bagian putihnya saja", "ambil bagian putihnya", "ambil putihnya saja", "ambil putihnya",
        "dilarutkan dengan air", "larutkan dengan air", "larutkan air",
        "bumbu halus", "bumbu ulek", "bumbu iris",
        "bahan marinasi", "bahan pelengkap", "bahan saus", "bahan pencelup",
        "bahan kering", "bahan basah", "bahan kuah", "bahan isi", "bahan olesan",
        "rebus", "direbus", "goreng", "digoreng", "sangrai", "bakar", "dibakar", "kukus", "dikukus", "panggang", "tumis", "oseng",
        "cuci bersih", "cuci", "tiriskan", "kupas", "dikupas",
        "buang biji", "buang tulang", "buang kulit", "buang kepala",
        "suwir-suwir", "suwir", "disuwir",
        "kocok lepas", "kocok", "larutkan", "seduh", "peras", "diperas", "parut", "diparut", "serut",
        "rendam", "direndam", "marinasi", "lumuri",
        "dadu", "fillet", "filet", "kotak", "serong", "tebal", "tipis", "panjang", "memanjang",
        "dingin", "hangat", "panas", "suhu ruang", "matang", "mentah", "segar",
        "yang sudah", "yang telah", "siap pakai", "siap saji"
    ]

    # -- 10. Kamus Sinonim Kanonik Kuliner -------------------------------------
    SYNONYM_MAP = {
        # Protective identity mappings
        "kecap manis": "kecap manis",
        "kecap asin": "kecap asin",
        "kecap ikan": "kecap ikan",
        "kecap inggris": "kecap inggris",
        "gula merah": "gula merah",
        "gula aren": "gula merah",
        "gula jawa": "gula merah",
        "gula pasir": "gula pasir",
        "gula putih": "gula pasir",
        "santan kental": "santan",
        "santan cair": "santan",
        "santan encer": "santan",
        "santan instan": "santan",
        "santan kara": "santan",
        "santen kara": "santan",
        "kara": "santan",
        "santen": "santan",
        "santan": "santan",

        # Protein
        "dada ayam fillet": "ayam",
        "ayam fillet": "ayam",
        "fillet ayam": "ayam",
        "dada ayam": "ayam",
        "paha ayam": "ayam",
        "sayap ayam": "ayam",
        "daging ayam": "ayam",
        "ayam potong": "ayam",
        "ayam kampung": "ayam",
        "ayam negeri": "ayam",
        "ayam": "ayam",
        "daging sapi": "daging sapi",
        "sapi has dalam": "daging sapi",
        "tetelan sapi": "daging sapi",
        "iga sapi": "daging sapi",
        "has dalam": "daging sapi",
        "sapi": "daging sapi",
        "daging kambing": "daging kambing",
        "iga kambing": "daging kambing",
        "kambing": "daging kambing",
        "telor": "telur",
        "telur ayam": "telur",
        "telur bebek": "telur",
        "telur puyuh": "telur",
        "kuning telur": "telur",
        "putih telur": "telur",
        "telor ayam": "telur",
        "tahu putih": "tahu",
        "tahu kuning": "tahu",
        "tahu cina": "tahu",
        "tahu pong": "tahu",
        "tahu sutra": "tahu",
        "tahu bulat": "tahu",
        "tahu": "tahu",
        "tempe papan": "tempe",
        "tempe gembus": "tempe",
        "tempe": "tempe",
        "udang kupas": "udang",
        "udang jerbung": "udang",
        "udang windu": "udang",
        "udang": "udang",
        "cumi cumi": "cumi",
        "cumi-cumi": "cumi",
        "cumi": "cumi",
        "ikan nila": "ikan",
        "ikan tongkol": "ikan",
        "ikan lele": "ikan",
        "ikan kembung": "ikan",
        "ikan mujair": "ikan",
        "ikan patin": "ikan",
        "ikan bandeng": "ikan",
        "ikan salmon": "ikan",
        "ikan tuna": "ikan",
        "ikan gurame": "ikan",
        "ikan kakap": "ikan",
        "ikan bawal": "ikan",
        "ikan tenggiri": "ikan",
        "ikan teri": "ikan",
        "ikan asin": "ikan",
        "ikan": "ikan",

        # Bumbu & Rempah
        "bamer": "bawang merah",
        "bw merah": "bawang merah",
        "bawang mrh": "bawang merah",
        "b merah": "bawang merah",
        "bwg merah": "bawang merah",
        "bawang merah kupas": "bawang merah",
        "bawang merah": "bawang merah",
        "baput": "bawang putih",
        "bw putih": "bawang putih",
        "bawang pth": "bawang putih",
        "b putih": "bawang putih",
        "bwg putih": "bawang putih",
        "bawang putih kupas": "bawang putih",
        "bawang putih": "bawang putih",
        "bawang bombai": "bawang bombay",
        "bombai": "bawang bombay",
        "bombay": "bawang bombay",
        "bawang bombay": "bawang bombay",
        "cabe": "cabai",
        "lombok": "cabai",
        "cabai merah": "cabai merah",
        "cabe merah": "cabai merah",
        "cabai merah besar": "cabai merah",
        "cabai merah keriting": "cabai merah",
        "cabe merah keriting": "cabai merah",
        "cabe merah besar": "cabai merah",
        "cabai rawit": "cabai rawit",
        "cabe rawit": "cabai rawit",
        "cabai rawit merah": "cabai rawit",
        "cabai rawit hijau": "cabai rawit",
        "cabe rawit merah": "cabai rawit",
        "cabe rawit hijau": "cabai rawit",
        "cengek": "cabai rawit",
        "cabai hijau": "cabai hijau",
        "cabe ijo": "cabai hijau",
        "cabe hijau": "cabai hijau",
        "cabai hijau besar": "cabai hijau",
        "cabai hijau keriting": "cabai hijau",
        "sereh": "serai",
        "sere": "serai",
        "serai": "serai",
        "laos": "lengkuas",
        "galangal": "lengkuas",
        "lengkuas": "lengkuas",
        "kunir": "kunyit",
        "turmerik": "kunyit",
        "kunyit": "kunyit",
        "miri": "kemiri",
        "kemiri": "kemiri",
        "tumbar": "ketumbar",
        "ketumbar": "ketumbar",
        "merica bubuk": "merica",
        "lada": "merica",
        "lada putih": "merica",
        "lada bubuk": "merica",
        "lada hitam": "merica",
        "merica": "merica",
        "jinten": "jintan",
        "jintan": "jintan",
        "pekak": "bunga lawang",
        "star anise": "bunga lawang",
        "bunga lawang": "bunga lawang",
        "daun jeruk purut": "daun jeruk",
        "daun limau": "daun jeruk",
        "daun jeruk": "daun jeruk",
        "sledri": "seledri",
        "daun seledri": "seledri",
        "daun sop": "seledri",
        "seledri": "seledri",
        "daun prei": "daun bawang",
        "loncang": "daun bawang",
        "oncang": "daun bawang",
        "bawang daun": "daun bawang",
        "daun pre": "daun bawang",
        "daun bawang": "daun bawang",
        "asem": "asam jawa",
        "asam": "asam jawa",
        "asem jawa": "asam jawa",
        "asam jawa": "asam jawa",
        "bumbu kacang": "bumbu kacang",
        "bumbu pecel": "bumbu kacang",
        "saus kacang": "bumbu kacang",

        # Sayuran
        "toge": "tauge",
        "taoge": "tauge",
        "kecambah": "tauge",
        "tauge": "tauge",
        "kol": "kubis",
        "kubis": "kubis",
        "kembang kol": "kembang kol",
        "bunga kol": "kembang kol",
        "sawi hijau": "sawi hijau",
        "caisim": "sawi hijau",
        "cesim": "sawi hijau",
        "pakcoy": "pakcoy",
        "pokcoy": "pakcoy",
        "pak choy": "pakcoy",
        "tomat merah": "tomat",
        "tomat hijau": "tomat",
        "tomat": "tomat",
        "timun": "mentimun",
        "ketimun": "mentimun",
        "mentimun": "mentimun",
        "terung": "terong",
        "terong": "terong",
        "jagung manis": "jagung",
        "jagung": "jagung",
        "labu siam": "labu siam",
        "manisa": "labu siam",
        "jipang": "labu siam",
        "wortel": "wortel",
        "kentang": "kentang",
        "buncis": "buncis",
        "bayam": "bayam",
        "kangkung": "kangkung",

        # Saus & Bahan Dapur
        "kecap": "kecap manis",
        "kecap bango": "kecap manis",
        "kecap manis sedaap": "kecap manis",
        "saus cabai": "saus sambal",
        "saus sambal": "saus sambal",
        "saos sambal": "saus sambal",
        "saori saus tiram": "saus tiram",
        "saori saos tiram": "saus tiram",
        "saos tiram": "saus tiram",
        "saus tiram": "saus tiram",
        "belacan": "terasi",
        "terasi": "terasi",
        "gula": "gula pasir",
        "royco": "kaldu bubuk",
        "masako": "kaldu bubuk",
        "totole": "kaldu bubuk",
        "kaldu jamur": "kaldu bubuk",
        "kaldu ayam": "kaldu bubuk",
        "kaldu sapi": "kaldu bubuk",
        "penyedap": "kaldu bubuk",
        "penyedap rasa": "kaldu bubuk",
        "micin": "kaldu bubuk",
        "vetsin": "kaldu bubuk",
        "msg": "kaldu bubuk",
        "minyak": "minyak goreng",
        "minyak sayur": "minyak goreng",
        "minyak kelapa": "minyak goreng",
        "mentega": "margarin",
        "blueband": "margarin",
        "blue band": "margarin",
        "terigu": "tepung terigu",
        "tepung protein sedang": "tepung terigu",
        "tepung protein tinggi": "tepung terigu",
        "maizena": "tepung maizena",
        "tepung jagung": "tepung maizena",
        "tapioka": "tepung tapioka",
        "aci": "tepung tapioka",
        "tepung kanji": "tepung tapioka",
        "tepung sagu": "tepung tapioka",
        "kanji": "tepung tapioka",
        "tepung panir": "tepung roti",
        "panir": "tepung roti",
        "mie instan": "mie",
        "mi telur": "mie",
        "mi": "mie",
        "mie telur": "mie",
        "bihun": "bihun",
        "soun": "soun",
    }

    def __init__(self):
        prep_sorted = sorted(self.PREPARATION_WORDS, key=len, reverse=True)
        self._prep_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(w) for w in prep_sorted) + r')\b', re.IGNORECASE)

        units_sorted = sorted(self.CULINARY_UNITS, key=len, reverse=True)
        self._units_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(w) for w in units_sorted) + r')\b', re.IGNORECASE)

        syn_sorted = sorted(self.SYNONYM_MAP.keys(), key=len, reverse=True)
        self._synonym_pattern = re.compile(r'\b(?:' + '|'.join(re.escape(w) for w in syn_sorted) + r')\b', re.IGNORECASE)

    def is_pantry_staple(self, term: str) -> bool:
        """Deteksi apakah bahan tergolong bahan pokok/bumbu dasar dapur."""
        if term in self.PANTRY_STAPLES:
            return True
        for staple in ["minyak goreng", "minyak", "air", "garam", "gula", "kaldu bubuk", "merica", "lada"]:
            if term == staple or term.startswith(staple + " "):
                return True
        return False

    def parse_ingredient_line(self, line: str) -> str:
        """
        Ekstraksi dan normalisasi satu baris bahan menjadi nama bahan kanonik.
        Contoh: '5 bh tahu kuning, belah 4' -> 'tahu'
        """
        if not isinstance(line, str):
            return ""

        text = line.lower().strip()

        # 1. Abaikan baris judul seksi resep (misal: 'Bahan Sambal :')
        if self.RE_SECTION_HEADER.search(text) or text.endswith(":"):
            return ""

        # 2. Buang alat non-pangan (misal: 'tusuk sate secukupnya')
        for tool in self.NON_FOOD_TERMS:
            if tool in text:
                return ""

        # 3. Hapus emoji & karakter visual unicode khusus
        text = re.sub(r'[\U00010000-\U0010ffff]', ' ', text)
        text = re.sub(r'[^\x00-\x7F\u00A0-\u024F\u1E00-\u1EFF½¼¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]', ' ', text)

        # 4. Hapus keterangan dalam tanda kurung berpasangan
        text = re.sub(r'\([^)]*\)', ' ', text)

        # 5. Hapus catatan percakapan Cookpad (misal: 'resep asli...', 'sesuai selera...')
        text = self.RE_CHATTER.sub(' ', text)

        # 6. Hapus klausa tujuan penggunaan (misal: 'untuk sate', 'untuk menumis')
        text = self.RE_PURPOSE.sub(' ', text)

        # 7. Pisahkan angka yang menempel langsung dengan huruf (misal: '65ml' -> '65 ml')
        text = re.sub(r'(\d+)\s*([a-zA-Z]+)', r'\1 \2', text)

        # 8. Normalisasi penanda reduplikasi 2 / ² (misal: 'sobek2' -> 'sobek sobek', 'potong²' -> 'potong potong')
        text = re.sub(r'(\b\w+)[2²]', r'\1 \1', text)

        # 9. Hapus angka, pecahan unicode, dan rentang takaran
        text = self.RE_FRACTIONS.sub(' ', text)
        text = self.RE_NUMBERS.sub(' ', text)

        # 10. Hapus pengubah ukuran fisik (misal: 'uk besar', 'ukuran sedang')
        text = self.RE_SIZES.sub(' ', text)

        # 11. Hapus kata kerja dan kondisi persiapan
        text = self._prep_pattern.sub(' ', text)

        # 12. Hapus satuan takaran kuliner
        text = self._units_pattern.sub(' ', text)

        # 13. Hapus seluruh tanda kurung gantung dan simbol sisa
        text = re.sub(r'[()\[\]{}+±*#~`^<>|=_/\\]', ' ', text)

        # 14. Hapus tanda baca umum
        text = re.sub(r"[,;:\.!?\-\u2013\u2014/'\"]+", " ", text)
        text = re.sub(r'\s+', ' ', text).strip()

        # 15. Terapkan pemetaan sinonim kanonik (dua tahap)
        text = self._apply_synonyms(text)
        text = self._apply_synonyms(text)

        # 16. Deduplikasi kata berulang berurutan
        text = re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', text)
        text = re.sub(r'\s+', ' ', text).strip()

        # 17. Validasi panjang minimum dan penolakan kata generik sisa
        if (len(text) <= 2 and text != "es") or text in (
            "bumbu", "bahan", "pelengkap", "topping", "isian",
            "olesan", "kuah", "sambal", "tambahan", "campuran",
            "halus", "campur", "aduk", "secukupnya", "resep", "di", "sp", "bp"
        ):
            return ""

        return text

    def _apply_synonyms(self, text: str) -> str:
        """Terapkan pemetaan sinonim greedy (longest match first)."""
        def _repl(match):
            return self.SYNONYM_MAP.get(match.group(0).lower(), match.group(0))
        return self._synonym_pattern.sub(_repl, text)

    def extract_ingredients_from_recipe(self, ingredient_lines: List[str]) -> Dict[str, Any]:
        """
        Proses seluruh daftar baris bahan satu resep.
        Hanya memecah alternatif bahan ('atau' / 'dan' / '+'), tidak memecah tanda koma.
        """
        all_ingredients = set()
        for raw_line in ingredient_lines:
            if not isinstance(raw_line, str):
                continue
            sublines = re.split(r'\b(?:atau|dan)\b|\+', raw_line, flags=re.IGNORECASE)
            for sub in sublines:
                parsed = self.parse_ingredient_line(sub)
                if parsed:
                    all_ingredients.add(parsed)

        core = {ing for ing in all_ingredients if not self.is_pantry_staple(ing)}
        if not core:
            core = all_ingredients.copy()

        # Bangun token IR komposit untuk indexing
        ir_tokens = set()
        for ingr in all_ingredients:
            words = ingr.split()
            if len(words) > 1:
                ir_tokens.add("_".join(words))  # e.g., bawang_merah
                for w in words:
                    if len(w) > 2:
                        ir_tokens.add(w)      # e.g., bawang, merah
            else:
                ir_tokens.add(ingr)

        return {
            "ingredients_all_set": all_ingredients,
            "ingredients_core_set": core,
            "ingredients_ir_tokens": ir_tokens,
            "ingredients_ir_text": " ".join(sorted(ir_tokens)),
        }

    def parse_query(self, query_string: str) -> Dict[str, Any]:
        """Parse query masukan pengguna (dipisahkan koma atau baris baru)."""
        parts = re.split(r'[,\n]+', query_string)
        lines = [p.strip() for p in parts if p.strip()]
        return self.extract_ingredients_from_recipe(lines)


PARSER = IndonesianIngredientParser()

if __name__ == "__main__":
    _test = PARSER.parse_ingredient_line("250 gr dada ayam fillet, potong dadu")
    print(f"  Test parse: '250 gr dada ayam fillet, potong dadu' -> '{_test}'")
    _test2 = PARSER.parse_query("2 potong ayam kampung, 5 siung bamer, 3 baput, cabe rawit, santen kara, daun jeruk")
    print("  Test query: 'ayam kampung, bamer, baput, cabe rawit, santen kara'")
    print(f"    - core: {_test2['ingredients_core_set']}")
    print(f"    - IR tokens: {_test2['ingredients_ir_tokens']}")
    print("[OK] IndonesianIngredientParser v2 siap digunakan.")

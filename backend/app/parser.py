"""
Indonesian Culinary NLP Parsing Engine
Extracted from SisaRasa IR Pipeline (Cell 5)
Handles:
- Indonesian fraction & unit normalization
- Preparation term stripping
- Synonym mapping & colloquial alias normalization
- Pantry staple separation
- Core ingredient identification
"""
import re
from typing import List, Dict, Set, Tuple, Any, Optional

# ==============================================================================
# CELL 5: IndonesianIngredientParser: Culinary NLP, Units, Prep Noise & Synonyms
# ==============================================================================

class IndonesianIngredientParser:
    """
    Parser bahan makanan Indonesia khusus IR:
    - Menghapus angka, satuan takaran, kata kerja persiapan
    - Menormalisasi sinonim ke bentuk kanonik
    - Memisahkan core vs pantry ingredients
    - Menghasilkan token komposit untuk indexing
    """

    # -- Pantry Staples --------------------------------------------------------
    PANTRY_STAPLES = frozenset({
        "air", "garam", "gula pasir", "minyak goreng", "kaldu bubuk", "merica",
    })

    # -- Regex: angka, pecahan, rentang ----------------------------------------
    RE_FRACTIONS = re.compile(r'[½¼¾⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞]')
    RE_NUMBERS = re.compile(
        r'\b\d+[\.,/]?\d*\s*[-\u2013\u2014]\s*\d+[\.,/]?\d*\b'
        r'|\b\d+\s*/\s*\d+\b'
        r'|\b\d+[\.,]\d+\b'
        r'|\b\d+\b'
    )

    # -- Satuan takaran kuliner (40+ entries) ----------------------------------
    CULINARY_UNITS = [
        "sendok makan", "sendok teh", "sendok", "sdm", "sdt", "sdk",
        "kilogram", "gram", "ons", "kg", "gr", "g",
        "mililiter", "liter", "ml", "cc", "l",
        "siung", "butir", "btr", "buah", "bh", "biji",
        "batang", "btg", "lembar", "lbr", "helai", "tangkai",
        "ruas", "jari", "cm",
        "bungkus", "bks", "sachet", "sct", "pak", "papan",
        "potong", "ptg", "iris",
        "ekor", "ikat", "genggam", "segenggam", "jumput", "sejumput",
        "gelas", "cangkir", "mangkok", "mangkuk", "piring", "kaleng", "botol",
        "tetes",
        "secukupnya", "sesuai selera", "optional", "opsional",
        "kurang lebih", "kira-kira", "sedikit",
        "setengah", "seperempat", "sepertiga",
    ]

    # -- Kata kerja / kondisi persiapan ----------------------------------------
    PREPARATION_WORDS = [
        "potong dadu", "potong korek api", "potong kecil", "potong-potong", "potong",
        "iris tipis", "iris serong", "iris halus", "iris kotak", "iris",
        "cincang halus", "cincang kasar", "cincang",
        "geprek", "memarkan", "dihaluskan", "haluskan", "ulek", "blender", "giling",
        "bumbu halus", "bumbu ulek", "bumbu iris", "bumbu kacang", "bumbu",
        "bahan marinasi", "bahan pelengkap", "bahan saus", "bahan pencelup",
        "bahan kering", "bahan basah", "bahan kuah", "bahan isi", "bahan olesan", "bahan",
        "rebus", "goreng", "sangrai", "bakar", "kukus", "panggang", "tumis", "oseng",
        "cuci bersih", "cuci", "tiriskan", "kupas", "buang biji", "buang tulang",
        "buang kulit", "buang kepala", "suwir-suwir", "suwir",
        "kocok lepas", "kocok", "larutkan", "seduh", "peras", "parut", "serut",
        "rendam", "marinasi", "lumuri",
        "dadu", "fillet", "filet",
        "dingin", "hangat", "panas", "suhu ruang", "matang", "mentah", "segar",
        "ukuran sedang", "ukuran besar", "ukuran kecil",
        "yang sudah", "yang telah", "untuk", "atau",
    ]

    # -- Kamus sinonim kuliner (Protective Keys + Canonical Mapping) -----------
    SYNONYM_MAP = {
        # Protective identity mappings (mencegah double replacement kata majemuk)
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
        "santan": "santan",
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
        "saori saus tiram": "saus tiram",
        "saori saos tiram": "saus tiram",
        "saos tiram": "saus tiram",
        "saus tiram": "saus tiram",
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
        "baput": "bawang putih",
        "bw putih": "bawang putih",
        "bawang pth": "bawang putih",
        "b putih": "bawang putih",
        "bwg putih": "bawang putih",
        "bawang bombai": "bawang bombay",
        "bombai": "bawang bombay",
        "bombay": "bawang bombay",
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
        "laos": "lengkuas",
        "galangal": "lengkuas",
        "kunir": "kunyit",
        "turmerik": "kunyit",
        "miri": "kemiri",
        "tumbar": "ketumbar",
        "merica bubuk": "merica",
        "lada": "merica",
        "lada putih": "merica",
        "lada bubuk": "merica",
        "lada hitam": "merica",
        "jinten": "jintan",
        "pekak": "bunga lawang",
        "star anise": "bunga lawang",
        "daun jeruk purut": "daun jeruk",
        "daun limau": "daun jeruk",
        "sledri": "seledri",
        "daun seledri": "seledri",
        "daun sop": "seledri",
        "daun prei": "daun bawang",
        "loncang": "daun bawang",
        "oncang": "daun bawang",
        "bawang daun": "daun bawang",
        "daun pre": "daun bawang",
        "asem": "asam jawa",
        "asam": "asam jawa",
        "asem jawa": "asam jawa",

        # Protein
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
        "tempe papan": "tempe",
        "tempe gembus": "tempe",
        "udang kupas": "udang",
        "udang jerbung": "udang",
        "udang windu": "udang",
        "cumi cumi": "cumi",
        "cumi-cumi": "cumi",

        # Sayuran
        "toge": "tauge",
        "taoge": "tauge",
        "kecambah": "tauge",
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
        "timun": "mentimun",
        "ketimun": "mentimun",
        "terung": "terong",
        "jagung manis": "jagung",
        "labu siam": "labu siam",
        "manisa": "labu siam",
        "jipang": "labu siam",

        # Saus & Bahan Dapur
        "santen": "santan",
        "kecap": "kecap manis",
        "kecap bango": "kecap manis",
        "kecap manis sedaap": "kecap manis",
        "saus cabai": "saus sambal",
        "belacan": "terasi",
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
        self._units_pattern = self._build_multiword_pattern(self.CULINARY_UNITS)
        self._prep_pattern = self._build_multiword_pattern(self.PREPARATION_WORDS)
        self._synonym_keys_sorted = sorted(self.SYNONYM_MAP.keys(), key=len, reverse=True)
        self._synonym_pattern = re.compile(
            r'\b(' + '|'.join(re.escape(k) for k in self._synonym_keys_sorted) + r')\b',
            re.IGNORECASE
        )

    @staticmethod
    def _build_multiword_pattern(word_list: list) -> re.Pattern:
        sorted_words = sorted(word_list, key=len, reverse=True)
        escaped = [re.escape(w) for w in sorted_words]
        return re.compile(r'\b(?:' + '|'.join(escaped) + r')\b', re.IGNORECASE)

    def parse_ingredient_line(self, line: str) -> str:
        """
        Dari satu baris bahan mentah, ekstrak nama bahan kanonik.
        Contoh: '250 gr dada ayam fillet, potong dadu' -> 'ayam'
        """
        if not isinstance(line, str):
            return ""

        text = line.lower().strip()

        # 1. Hapus tanda kurung dan isinya
        text = re.sub(r'\([^)]*\)', ' ', text)

        # 2. Hapus angka, pecahan unicode, dan rentang takaran
        text = self.RE_FRACTIONS.sub(' ', text)
        text = self.RE_NUMBERS.sub(' ', text)

        # 3. CRITICAL: Hapus kata kerja/kondisi persiapan SEBELUM satuan takaran
        text = self._prep_pattern.sub(' ', text)

        # 4. Hapus satuan takaran kuliner
        text = self._units_pattern.sub(' ', text)

        # 5. Hapus tanda baca
        text = re.sub(r"[,;:\.!?\-\u2013\u2014/'\"]+", " ", text)

        # 6. Normalisasi whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # 7. Terapkan sinonim: Pass 1 (pemetaan langsung)
        text = self._apply_synonyms(text)

        # 8. Terapkan sinonim: Pass 2 (merapikan kata hasil reduksi)
        text = self._apply_synonyms(text)

        # 9. Deduplikasi kata berulang berurutan (mencegah 'manis manis', 'pasir pasir')
        text = re.sub(r'\b(\w+)(?:\s+\1\b)+', r'\1', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _apply_synonyms(self, text: str) -> str:
        """Terapkan pemetaan sinonim greedy (longest match first)."""
        def _repl(match):
            return self.SYNONYM_MAP.get(match.group(0).lower(), match.group(0))
        return self._synonym_pattern.sub(_repl, text)

    def extract_ingredients_from_recipe(self, ingredient_lines: List[str]) -> Dict[str, Any]:
        """
        Proses seluruh daftar baris bahan satu resep dengan pemecahan alternatif 'atau'/'dan'.
        """
        all_ingredients = set()
        for raw_line in ingredient_lines:
            if not isinstance(raw_line, str):
                continue
            # Pecah baris jika mengandung alternatif bahan ('atau', 'dan', koma, slash)
            sublines = re.split(r'\b(?:atau|dan)\b|[,/]', raw_line, flags=re.IGNORECASE)
            for sub in sublines:
                parsed = self.parse_ingredient_line(sub)
                if parsed and len(parsed) > 1 and parsed not in ("bumbu", "bahan"):
                    all_ingredients.add(parsed)

        core = all_ingredients - self.PANTRY_STAPLES
        if not core:
            core = all_ingredients.copy()

        # Bangun IR tokens: token komposit underscore + token kata dasar
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
        """Parse query pengguna (dipisahkan koma atau baris baru)."""
        parts = re.split(r'[,\n]+', query_string)
        lines = [p.strip() for p in parts if p.strip()]
        return self.extract_ingredients_from_recipe(lines)


PARSER = IndonesianIngredientParser()

if __name__ == "__main__":
    # Pengujian Unit NLP Parser
    _test = PARSER.parse_ingredient_line("250 gr dada ayam fillet, potong dadu")
    print(f"  Test parse: '250 gr dada ayam fillet, potong dadu' -> '{_test}'")
    _test2 = PARSER.parse_query("2 potong ayam kampung, 5 siung bamer, 3 baput, cabe rawit, santen kara, daun jeruk")
    print(f"  Test query: 'ayam kampung, bamer, baput, cabe rawit, santen kara'")
    print(f"    - core: {_test2['ingredients_core_set']}")
    print(f"    - IR tokens: {_test2['ingredients_ir_tokens']}")
    print("[OK] IndonesianIngredientParser siap digunakan.")


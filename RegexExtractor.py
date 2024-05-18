import re
import pickle
import sqlite3 
import geopy
from geopy.geocoders import Nominatim
from collections import defaultdict, Counter

class RegexClassifier(object):
    
    def __init__(self):
        self.resources = r"C:\Users\Mohammad\Desktop\address_extractor\resources"
        self.__load_dicts()
        
        self.match_address()
        self.match_email()
        self.match_url()
        self.match_phone()
        
        self.create_db()
        self.add_pattern('address', self.address_regex)
        self.add_pattern('email', self.email_regex)
        self.add_pattern('url', self.url_regex)
        self.add_pattern('phone', self.phone_regex)
        
    def __load_dicts(self):
        with open("{0}/ambiguity_countries.csv".format(self.resources), "r", encoding='utf8') as f:
            self.ambiguity_countries = {
                line.replace("\n", "").strip().split(",")[0]:
                int(line.replace("\n", "").strip().split(",")[1])
                for line in f.readlines()}
        with open("{0}/countries.pickle".format(self.resources), "rb") as f:
            countries = [str(num) for num in pickle.load(f)]
            self.countries = "\\b(" + '|'.join(countries) + ")\\b"

        with open("{0}/provinces.pickle".format(self.resources), "rb") as f:
            province = [str(num) for num in pickle.load(f)]
            self.province = "\\b(" + '|'.join(province) + ")\\b"

        with open("{0}/cities_phone.pickle".format(self.resources), "rb") as f:
            cities_phone = [str(num) for num in pickle.load(f)]
            self.cities_phone_prefix = "(" + '|'.join(cities_phone) + ")"

        with open("{0}/cities_name.pickle".format(self.resources), "rb") as f:
            self.cities = [str(num) for num in pickle.load(f)]
            self.cities = "\\b(" + '|'.join(self.cities) + ")\\b"

        with open("{0}/places.pickle".format(self.resources), "rb") as f:
            places = [str(num) for num in pickle.load(f)]
            self.places = "\\b(" + '|'.join(places) + ")\\b"
 
            
    def standardize_query(self, text: str):
        words = text.split(" ")
        for i in range(len(words)):
            if words[i] in self.abbreviates:
                words[i] = self.abbreviates[words[i]]
            elif "." in words[i]:
                tokens = words[i].split(".")
                if len(tokens) == 1 and tokens[0] in self.abbreviates:
                    words[i] = self.abbreviates[tokens[0]]
                elif len(tokens) == 2 and tokens[0] in self.abbreviates and\
                tokens[1] not in self.abbreviates:
                    words[i] = self.abbreviates[tokens[0]] + " " + tokens[1]
        return ' '.join(words).lstrip().rstrip().strip()

    def normalize_number(self, text: str):
        persian_numbers = "۰۱۲۳۴۵۶۷۸۹" 
        english_numbers = "0123456789"
        arabic_numbers = "٠١٢٣٤٥٦٧٨٩"

        translation_from_persian = str.maketrans(persian_numbers, english_numbers)
        translation_from_arabic = str.maketrans(arabic_numbers, english_numbers)

        return text.translate(translation_from_persian).translate(translation_from_arabic)

    def specify_ambiguity_locations(self, text: str):
        signs = list(self.abbreviates.keys()) +\
                list(self.abbreviates.values()) +\
                self.ez_address_identifier.split("|") +\
                self.non_starter_addresskeywords.split("|") +\
                self.relational_addresskeywords.split("|") +\
                self.start_addresskeywords.split("|")

        words = text.split(" ")
        for i in range(len(words)) :
            if words[i] in self.ambiguity_countries and\
            self.ambiguity_countries[words[i]] == 0:
                if not list(set(signs) & set([words[i-2], words[i-1], words[i+1], words[i+2]])):
                    words[i] = "1**1" + words[i] + "1**1"

        return ' '.join(words)
    
    def classify_message_length(self, text: str):
        words = text.split(" ")
        if len(words) <= 20:
            return "short message"
        else:
            return "long message"

    
    def get_location_details(self, address):
        geolocator = Nominatim(user_agent="my_app")
        try:
            location = geolocator.geocode(address)
            if location:
                return {'lat': location.latitude, 'lon': location.longitude}
        except:
            pass
        return None

    def match_address(self):
        self.abbreviates = {
            "پ": "پلاک",
            "خ": "خیابان",
            "م": "میدان",
        }
        self.ez_address_identifier = "ادرس|آدرس|نشانی"
        self.non_starter_addresskeywords = "منطقه|طبقه|کوچه|بن‌بست|بنبست|بن بست|پلاک|واحد|بلوک|برج"
        self.non_starter_address_keywords_regex =\
             r"\b(منطقه|طبقه|کوچه|بن‌بست|بنبست|بن بست|پلاک|واحد|بلوک|برج)\b"
        self.relational_addresskeywords = "جنب|رو به رو|رو به روی|روبه‌رو|روبه‌روی|روبروی|روبرو|بالاتر از|پایین‌تر از|پایین‌ تر از|قبل از|بعد از|نبش"
        self.relational_address_keywords_regex =\
             r"\b(جنب|رو به رو|رو به روی|روبه‌رو|روبه‌روی|روبروی|روبرو|بالاتر از|پایین‌تر از|پایین‌ تر از|قبل از|بعد از|نبش)\b"
        self.separators = "،|-|,"
        self.start_addresskeywords = "تقاطع|منطقه‌ی|بعد از|منطقه ی|دانشگاه|مدرسه|منطقه|خیابون|خیابان|بلوار|میدون|میدان|بزرگ‌راه|بزرگراه|آزادراه|آزاد راه|اتوبان|محله‌ی|محله ی|جاده|محله|کوی|چهارراه|چهار راه|سه‌راه|سراه|سه‌ راه|شهر|کشور|استان|شهرستان|دهستان|روستای|شهرک|حومه‌ی|حومه ی|حومه|پل"
        self.start_address_keywords_regex =\
            r"\b(تقاطع|منطقه‌ی|بعد از|منطقه ی|منطقه|خیابون|خیابان|بلوار|میدون|میدان|بزرگ‌راه|بزرگراه|آزادراه|آزاد راه|اتوبان|محله‌ی|محله ی|جاده|محله|کوی|چهارراه|چهار راه|سه‌راه|سراه|سه‌ راه|شهر|کشور|استان|شهرستان|دهستان|روستای|شهرک|حومه‌ی|حومه ی|حومه|پل)\b"
        self.locations = f"{self.countries}|{self.cities}|{self.province}"
        self.middle_address_keywords = f"{self.start_address_keywords_regex}|{self.non_starter_address_keywords_regex}|{self.relational_address_keywords_regex}"
        self.starter_keywords = f"({self.ez_address_identifier}|{self.start_address_keywords_regex}|{self.locations})"
        self.pattern = f"({self.starter_keywords})([^\\.]{{{{{{spaces_count}}}}}}({self.middle_address_keywords}|{self.separators})){{{{{{keyword_count}}}}}}( *({self.places})? *\w*)"
        self.address_regex = f'({self.pattern.format(keyword_count="1,10", spaces_count="0,20")})|({self.locations})'

    def match_email(self):
        self.email_regex = r"\b(\w+([-+(\.|\[dot\])']\w+)*(@|\[at\])\w+([-(\.|\[dot\])]\w+)*(\.|\[dot\])\w+([-(\.|\[dot\])]\w+)*)\b"
        
    def match_url(self):
        self.url_regex = r"\b((https|http|ftp):\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)\b"

    def match_phone(self):
        self.cities_phone_prefix = "(41|44|45|31|84|77|21|38|51|56|58|61|24|23|54|71|26|25|28|87|34|83|74|17|13|66|11|86|76|81)"
        mobile_pattern = "(0|((\+98)[- ]?|(\(\+98\))[- ]?))?9([01239][0-9])[- ]?[0-9]{3}[- ]?[0-9]{4}"
        phone_pattern = f"(0|(((\+98)|(\(\+98\)))[- ]?))?(({self.cities_phone_prefix}|(\({self.cities_phone_prefix}\)))[- ]?)?[0-9]{{1,4}} ?[0-9]{{4}}"
        phone_without_country_pattern = f"(((0?{self.cities_phone_prefix})|(\(0?{self.cities_phone_prefix}\)))[- ]?)?[0-9]{{1,4}} ?[0-9]{{4}}"  # ----->   (021)7782540555
        phone_three_digit = "\\b(110|112|113|114|115|123|125|111|116|118|120|121|122|124|129|131|132|133|134|136|137|141|162|190|191|192|193|194|195|197|199)\\b"
        phone_three_digit_word = " صد و ده|صد و دوازده|صد و سیزده|صد و چهارده|صد و پانزده|صد و بیست و سه|صد و بیست و پنج|صد و یازده|صد و شانزده|صد و هجده|صد و بیست|صد و بیست و یک|صد و بیست و دو|صد و بیست و چهار|صد و بیست و نه|صد و سی یک|صد و سی و دو|صد و سی و سه|صد و سی و چهار|صد و سی و شش|صد و سی هفت|صد و چهل و یک|صد و شصت و دو|صد و نود|صد و نود و یک|صد و نود و دو|صد و نود و سه|صد و نود و چهار|صد و نود و پنج|صد و نود و هفت|صد و نود و نه"
        phone_four_digit = f"((0?{self.cities_phone_prefix}|\(0?{self.cities_phone_prefix}\))[- ]?)[1-9][0-9]{{3}}|([3-9]\d{{3}}|2[1-9]\d{{2}})"
        
        self.phone_regex = f"(({mobile_pattern})|({phone_pattern})|({phone_without_country_pattern})|({phone_three_digit})|({phone_three_digit_word})|({phone_four_digit}))"
    
    def load_regex(self):
        conn = sqlite3.connect('regexDB.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patterns")
        regex_rules = {name: pattern for name, pattern in cursor.fetchall()}
        conn.close()
        
    def create_db(self):
        conn = sqlite3.connect('regexDB.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS patterns
                 (name text, pattern text)''')
        c.execute("DELETE FROM patterns")
        conn.commit()
        conn.close()
        
    def add_pattern(self, name, pattern):
        conn = sqlite3.connect('regexDB.db')
        c = conn.cursor()
        c.execute("INSERT INTO patterns VALUES (?,?)", (name, pattern))
        conn.commit()
        conn.close()

    def match_patterns(self, text: str):
        string = self.standardize_query(text)
        string = self.specify_ambiguity_locations(string)
        conn = sqlite3.connect('regexDB.db')
        c = conn.cursor()
        c.execute("SELECT * FROM patterns")
        patterns = c.fetchall()
        matches = {}
        for name, pattern in patterns:
            matches[name] = []
            for match in (re.finditer(pattern, string)):
                matches[name].append(match.group())
                matches[name].append(match.span())
                if name == 'address':
                    try:
                        location = self.get_location_details(match.group())
                        if location:
                            matches[name].append(f"(Latitude: {location['lat']}, Longitude: {location['lon']})")
                    except:
                        pass
            matches['message_length'] = self.classify_message_length(string)
        conn.close()

#        output = []
#         for name, match_list in matches.items():
#             if match_list:
#                 output.append(f"{name.capitalize()}:")
#                 for match in match_list:
#                     output.append(f"- {match}")

#         return "\n".join(output)
        return matches

    def match_input_pattern(self, text, pattern):
        string = self.standardize_query(text)
        string = self.specify_ambiguity_locations(string)
        matches = []
        for match in (re.finditer(pattern, string)):
            matches.append([match.group(), match.span()])
        return matches


    def extract_regex_pattern(self, examples):
        # Tokenize the examples and analyze character positions
        tokenized_examples = [list(example) for example in examples]
        max_length = max(len(example) for example in examples)

        # Initialize data structures for analysis
        position_char_counts = [Counter() for _ in range(max_length)]
        length_counts = Counter(len(example) for example in examples)

        for example in tokenized_examples:
            for i, char in enumerate(example):
                position_char_counts[i][char] += 1

        # Initialize an empty pattern list
        pattern = []

        # Analyze character positions for optional and repeated characters
        i = 0
        while i < max_length:
            char_count = position_char_counts[i]
            total_examples = len(examples)

            if len(char_count) == 1:
                # Single unique character at this position
                char = next(iter(char_count))
                if char_count[char] == total_examples:
                    # Mandatory character
                    pattern.append(re.escape(char))
                    i += 1
                else:
                    # Optional character
                    pattern.append(re.escape(char) + '?')
                    i += 1
            else:
                # Multiple characters at this position, need to generalize
                if all(i < len(example) and example[i].isdigit() for example in tokenized_examples):
                    # Check for repeated digits
                    j = i
                    while j < max_length and all(j < len(example) and example[j].isdigit() for example in tokenized_examples):
                        # print(f"i: {i}, j: {j}, example[j]: {example[j]}")
                        j += 1
                    repeat_count = j - i
                    if repeat_count > 1:
                        pattern.append(r'\d{' + str(repeat_count) + '}')
                    else:
                        pattern.append(r'\d')
                    i = j
                elif all(i < len(example) and example[i].isalpha() for example in tokenized_examples):
                    # Check for repeated letters
                    j = i
                    while j < max_length and all(j < len(example) and example[j].isalpha() for example in tokenized_examples):
                        # print(f"i: {i}, j: {j}, example[j]: {example[j]}")
                        j += 1
                    repeat_count = j - i
                    if repeat_count > 1:
                        pattern.append(r'[a-zA-Z]{' + str(repeat_count) + '}')
                    else:
                        pattern.append(r'[a-zA-Z]')
                    i = j
                else:
                    # Handle mixed or special characters
                    j = i
                    while j < max_length and all(j < len(example) for example in tokenized_examples) and not all(example[j].isalnum() for example in tokenized_examples):
                        # print(f"i: {i}, j: {j}, example[j]: {example[j]}")
                        j += 1
                    repeat_count = j - i
                    if repeat_count > 1:
                        pattern.append('.{' + str(repeat_count) + '}')
                    else:
                        pattern.append('.')
                        if i == j:
                            j += 1
                    i = j

        return ''.join(pattern)
import re
import enum
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

DIRSEARCH_URL = 'https://webapps.mines.edu/DirSearch/Home/search'
MPAPI_URL = 'https://mastergo.mines.edu/mpapi'
_username_p = re.compile("^[A-Za-z0-9]+$")

class Who(enum.Enum):
    ALL = 0
    FACULTY = 1
    ADMIN = 2
    CLASSIFIED = 3
    OTHER_STAFF = 4
    STUDENT_EMPLOYEES = 5

class Department(enum.Enum):
    ALL = 0
    ACADEMICAFFAIRS = "31"
    ADMIN = "32"
    ADMISSIONS = "39"
    ALUMNI = "AL"
    AMS = "Dr71"
    BLASTERCARD = "CO"
    BOOKSTORE = "BK"
    BUDGET = "38"
    CCIT = "41"
    CONSTRUCTION = "Dr26"
    CAREER = "PL"
    CASA = "Dr81"
    CBE = "02"
    CHEMISTRY = "03"
    CHIEF_OF_STAFF = "Dr32"
    CEE = "Dr72"
    CASE = "Dr85"
    CERSE = "Dr86"
    CECS = "Dr75"
    CCAC = "C1"
    CERI = "IE"
    CGS = "Dr84"
    CONTROLLER = "37"
    COUNSELING = "Dr78"
    MAIL = "63"
    DIVERSITY = "Dr76"
    EB = "11"
    EE = "Dr73"
    EG = "01"
    SAFETY = "29"
    ENVIRONMENT = "04"
    EPICS = "16"
    FACILITIES = "48"
    FINANCIAL_AID = "43"
    SODEXO = "AR"
    CSM_FOUNDATION = "FN"
    GE = "05"
    GEOLOGY_MUESEM = "MU"
    GP = "06"
    GS = "36"
    GREEN_CENTER_EVENTS = "61"
    HR = "47"
    LAIS = "17"
    INTERNATIONAL_PROGRAMS = "A1"
    INTERNATIONAL_OFFICE = "A2"
    CLUB_SPORTS = "Dr70"
    LEGAL = "27"
    LB = "46"
    ME = "Dr74"
    MT = "09"
    MS = "10"
    MN = "12"
    MEP = "97"
    ORC = "AU"
    PE = "13"
    ATHLETICS = "14"
    PHYSICS = "15"
    PRESIDENTS_OFFICE = "30"
    PUBLIC_RELATIONS = "49"
    PUBLIC_SAFETY = "50"
    PURCHASING = "57"
    REGISTRAR = "52"
    REMRSEC = "Dr30"
    RESEARCH_ADMIN = "54"
    TECHNOLOGY_TRANSFER = "AC"
    SPECIAL_PROGRAMS = "71"
    SAO = "56"
    SHIP = "Dr80"
    HEALTH_CENTER = "45"
    HOUSING = "44"
    STUDENT_LIFE = "35"
    STUDENT_SERVICES = "Dr77"
    WAVE_PHENOMENA = "CE"
    WISEM = "Dr69"

class Name:
    ds_name_p = re.compile(r'^\s*(?P<last>[^,]*?)\s*,\s+(?P<first>.*?)\s*(?:\(\s*(?P<nick>.*?)\s*\)\s*)?$')

    def __init__(self, ds_name):
        m = self.ds_name_p.match(ds_name)
        for k, v in m.groupdict(default='').items():
            setattr(self, k, v)

    @property
    def pfirst(self):
        return self.nick or self.first

    @property
    def nickp(self):
        if not self.nick:
            return self.nick
        return ' ({})'.format(self.nick)

    def strfname(self, fmt):
        return fmt.format(first=self.first, last=self.last, nick=self.nick, pfirst=self.pfirst, nickp=self.nickp)

    def __str__(self):
        return self.strfname('{first}{nickp} {last}')

    def __repr__(self):
        return self.strfname("Name(first='{first}', last='{last}', nick='{nick}')")

    def __eq__(self, other):
        return (self.last == other.last
                and self.first == other.first
                and self.nick == other.nick)

    def __hash__(self):
        return hash(str(self))

class Person:
    email_p = re.compile('^([A-Za-z0-9_-]+)@(?:mymail\.)?mines\.edu')

    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def from_soup(cls, soup):
        info = {}
        big = soup.find('big')
        info['name'] = Name(big.get_text())
        if big.find('a'):
            info['homepage'] = str(big.find('a').href)
        s = big.parent
        while s.name != 'div':
            s = s.next_sibling
            if s.name == 'br':
                continue
            if s.name == 'a':
                info['department'] = s.get_text()
                info['department_url'] = str(s.href)
        indent = soup.find(id='Indented')
        if indent:
            for elems in _iterate_breaks(indent):
                if len(elems) == 2:
                    key = str(elems[0]).partition(':')[0].lower().strip().replace(' ', '_')
                    val = elems[1].get_text().strip()
                    info[key] = val
        return cls(**info)

    @property
    def username(self):
        if hasattr(self, 'business_email'):
            m = self.email_p.match(self.business_email)
            if m:
                return m.group(1).lower()
        return None

    @property
    def desc(self):
        return ', '.join(
            getattr(self, attr)
                for attr in ("classification", "department")
                if hasattr(self, attr)
        )

    def __repr__(self):
        return "Person(name={!r}, ...)".format(self.name)

    def __eq__(self, other):
        return (self.username == other.username
                or self.name == other.name)

    def __hash__(self):
        return hash(self.username or self.name)

def _iterate_breaks(elem):
    elems = []
    for e in elem.children:
        if e.name == 'br':
            yield elems
            elems = []
        elif not str(e).strip():
            continue
        else:
            elems.append(e)
    if elems:
        yield elems

def _download_from_detail(url):
    r = requests.get(url)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    return Person.from_soup(soup)

def search_by_name(query, who=Who.ALL, departments=(Department.ALL, ), url=DIRSEARCH_URL, executor=None):
    server_base = re.sub(r'^(https?://[^/]+).*$', r'\1', url)
    data = {'SearchString': query, 'SelectedWhoID': who.value, 'btnSubmit': 'Search'}
    if Department.ALL in departments:
        data['AllDepartments'] = 'true'
        data['SelectedDepartments'] = '39'
    else:
        data['AllDepartments'] = 'false'
        data['SelectedDepartments'] = [d.value for d in departments]
    r = requests.get(url, params=data)
    r.raise_for_status()
    if 'No records found' in r.text:
        return
    soup = BeautifulSoup(r.text, "html.parser")
    if '/DirSearch/Home/detail/' in r.text:
        futures = []
        need_to_shutdown = False
        if not executor:
            executor = ThreadPoolExecutor()
            need_to_shutdown = True
        for a in soup.find_all('a'):
            if a.get('href', '').startswith('/DirSearch/Home/detail/'):
                futures.append(executor.submit(_download_from_detail, server_base + a["href"]))
        for f in futures:
            yield f.result()
        if need_to_shutdown:
            executor.shutdown()
    else:
        yield Person.from_soup(soup)

def search_by_partial(query, executor=None):
    need_to_shutdown = False
    if not executor:
        executor = ThreadPoolExecutor()
        need_to_shutdown = True
    query = query.lower()
    r = requests.get("{}/partial/{}".format(MPAPI_URL, query))
    r.raise_for_status()
    results = set()
    futures = []
    for user in r.json()["results"]:
        futures.append(
            executor.submit(
                list, search_by_name("{} {}".format(user["first"], user["sn"]), executor=executor)
            )
        )
    for future in futures:
        rs = future.result()
        for result in rs:
            if not result.username or query in result.username:
                results.add(result)
                yield result
    if need_to_shutdown:
        executor.shutdown()

def search(query, executor=None):
    results = set()
    if _username_p.match(query):
        for result in search_by_partial(query, executor=executor):
            if result not in results:
                results.add(result)
                yield result
    for result in search_by_name(query, executor=executor):
        if result not in results:
            yield result


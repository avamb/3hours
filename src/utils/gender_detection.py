"""
MINDSETHAPPYBOT - Gender Detection Utility
Detects user gender from first name, last name, or username
"""
import logging
from typing import Optional, Literal

logger = logging.getLogger(__name__)

# Gender type
Gender = Literal['male', 'female', 'unknown']

# Common Russian/Slavic male names
MALE_NAMES_RU = {
    # Common male names
    'александр', 'алексей', 'андрей', 'антон', 'артём', 'артем', 'богдан', 'борис',
    'вадим', 'валентин', 'валерий', 'василий', 'виктор', 'виталий', 'владимир',
    'владислав', 'вячеслав', 'геннадий', 'георгий', 'глеб', 'григорий', 'давид',
    'даниил', 'данил', 'денис', 'дмитрий', 'евгений', 'егор', 'иван', 'игорь',
    'илья', 'кирилл', 'константин', 'леонид', 'максим', 'марк', 'михаил',
    'никита', 'николай', 'олег', 'павел', 'пётр', 'петр', 'роман', 'руслан',
    'сергей', 'станислав', 'степан', 'тимофей', 'тимур', 'фёдор', 'федор',
    'эдуард', 'юрий', 'ярослав',
    # Diminutives
    'саша', 'лёша', 'леша', 'андрюша', 'антоша', 'тёма', 'тема', 'боря', 'вадик',
    'валера', 'вася', 'витя', 'влад', 'слава', 'гена', 'гоша', 'жора', 'глеб',
    'гриша', 'даня', 'дима', 'женя', 'егорка', 'ваня', 'игорёк', 'илюша',
    'кирюша', 'костя', 'лёня', 'леня', 'макс', 'миша', 'коля', 'паша', 'петя',
    'рома', 'серёжа', 'сережа', 'стас', 'стёпа', 'степа', 'тима', 'федя', 'юра',
}

# Common Russian/Slavic female names
FEMALE_NAMES_RU = {
    # Common female names
    'александра', 'алина', 'алиса', 'алла', 'анастасия', 'анна', 'валентина',
    'валерия', 'варвара', 'вера', 'вероника', 'виктория', 'галина', 'дарья',
    'диана', 'евгения', 'екатерина', 'елена', 'елизавета', 'жанна', 'зоя',
    'инна', 'ирина', 'карина', 'кристина', 'ксения', 'лариса', 'лидия',
    'любовь', 'людмила', 'маргарита', 'марина', 'мария', 'надежда', 'наталья',
    'наталия', 'нина', 'оксана', 'ольга', 'полина', 'раиса', 'светлана',
    'софия', 'софья', 'тамара', 'татьяна', 'ульяна', 'юлия', 'яна',
    # Diminutives
    'саша', 'алинка', 'настя', 'аня', 'аннушка', 'валя', 'лера', 'варя',
    'вика', 'галя', 'даша', 'дашенька', 'катя', 'лена', 'лиза', 'ира', 'иришка',
    'ксюша', 'лариска', 'люба', 'люда', 'рита', 'маша', 'машенька', 'надя',
    'наташа', 'оля', 'оленька', 'света', 'соня', 'сонечка', 'тома', 'таня',
    'юля', 'юленька', 'янка',
}

# Common English/International male names
MALE_NAMES_EN = {
    'adam', 'alan', 'albert', 'alex', 'alexander', 'alfred', 'andrew', 'anthony',
    'arthur', 'benjamin', 'bill', 'bob', 'brian', 'bruce', 'carl', 'charles',
    'chris', 'christian', 'christopher', 'daniel', 'david', 'dennis', 'donald',
    'douglas', 'edward', 'eric', 'eugene', 'frank', 'fred', 'gary', 'george',
    'gerald', 'gordon', 'gregory', 'harold', 'harry', 'henry', 'howard', 'jack',
    'james', 'jason', 'jeff', 'jeffrey', 'jerry', 'jim', 'jimmy', 'joe', 'john',
    'johnny', 'jonathan', 'joseph', 'joshua', 'justin', 'keith', 'kenneth',
    'kevin', 'larry', 'lawrence', 'leo', 'leonard', 'louis', 'mark', 'martin',
    'matthew', 'max', 'michael', 'mike', 'nathan', 'nicholas', 'nick', 'oliver',
    'patrick', 'paul', 'peter', 'philip', 'ralph', 'raymond', 'richard', 'robert',
    'roger', 'ronald', 'roy', 'russell', 'ryan', 'samuel', 'scott', 'sean',
    'simon', 'stephen', 'steve', 'steven', 'terry', 'thomas', 'tim', 'timothy',
    'tom', 'tony', 'victor', 'walter', 'wayne', 'william', 'yitzhak', 'yitzchak',
}

# Common English/International female names
FEMALE_NAMES_EN = {
    'alice', 'amanda', 'amy', 'andrea', 'angela', 'anna', 'anne', 'barbara',
    'betty', 'brenda', 'carol', 'caroline', 'catherine', 'charlotte', 'cheryl',
    'christina', 'christine', 'cynthia', 'deborah', 'denise', 'diana', 'diane',
    'donna', 'dorothy', 'elizabeth', 'ellen', 'emily', 'emma', 'evelyn', 'frances',
    'gloria', 'grace', 'hannah', 'helen', 'irene', 'jane', 'janet', 'jennifer',
    'jessica', 'joan', 'judy', 'julia', 'julie', 'karen', 'katherine', 'kathleen',
    'kelly', 'kimberly', 'laura', 'lauren', 'linda', 'lisa', 'lori', 'louise',
    'margaret', 'maria', 'marie', 'marilyn', 'martha', 'mary', 'melissa', 'michelle',
    'nancy', 'natalie', 'nicole', 'pamela', 'patricia', 'paula', 'rachel', 'rebecca',
    'rose', 'ruth', 'samantha', 'sandra', 'sara', 'sarah', 'sharon', 'shirley',
    'sophia', 'stephanie', 'susan', 'teresa', 'theresa', 'tiffany', 'valeria',
    'valerie', 'victoria', 'virginia', 'wendy',
}

# Hebrew male names
MALE_NAMES_HE = {
    'אברהם', 'יצחק', 'יעקב', 'משה', 'אהרן', 'דוד', 'שלמה', 'יוסף', 'בנימין',
    'דניאל', 'אליהו', 'נתן', 'שמואל', 'גדעון', 'נועם', 'עומר', 'אורי', 'יונתן',
    'yitzhak', 'yitzchak', 'moshe', 'david', 'shlomo', 'avraham', 'abraham',
    'yosef', 'joseph', 'binyamin', 'benjamin', 'eliyahu', 'eli', 'natan', 'nathan',
    'shmuel', 'samuel', 'gideon', 'noam', 'omer', 'uri', 'yonatan', 'jonathan',
}

# Common Ukrainian names
MALE_NAMES_UK = {
    'олександр', 'олексій', 'андрій', 'антон', 'артем', 'богдан', 'борис',
    'вадим', 'валентин', 'валерій', 'василь', 'віктор', 'віталій', 'володимир',
    'в\'ячеслав', 'геннадій', 'георгій', 'григорій', 'давид', 'данило', 'денис',
    'дмитро', 'євген', 'ігор', 'іван', 'ілля', 'кирило', 'костянтин', 'леонід',
    'максим', 'марко', 'михайло', 'микита', 'микола', 'олег', 'павло', 'петро',
    'роман', 'руслан', 'сергій', 'станіслав', 'степан', 'тарас', 'тимофій',
    'федір', 'юрій', 'ярослав',
}

FEMALE_NAMES_UK = {
    'олександра', 'аліна', 'аліса', 'алла', 'анастасія', 'анна', 'валентина',
    'валерія', 'варвара', 'віра', 'вероніка', 'вікторія', 'галина', 'дарина',
    'дар\'я', 'діана', 'євгенія', 'катерина', 'олена', 'єлизавета', 'жанна',
    'зоя', 'інна', 'ірина', 'каріна', 'крістіна', 'ксенія', 'лариса', 'лідія',
    'любов', 'людмила', 'маргарита', 'марина', 'марія', 'надія', 'наталія',
    'ніна', 'оксана', 'ольга', 'поліна', 'раїса', 'світлана', 'софія',
    'тамара', 'тетяна', 'уляна', 'юлія', 'яна',
}

# German names
MALE_NAMES_DE = {
    'hans', 'peter', 'michael', 'thomas', 'andreas', 'stefan', 'christian',
    'markus', 'martin', 'frank', 'klaus', 'jürgen', 'jurgen', 'wolfgang',
    'helmut', 'karl', 'heinrich', 'friedrich', 'walter', 'werner', 'franz',
    'matthias', 'ralf', 'dieter', 'günter', 'gunter', 'bernd', 'uwe', 'manfred',
}

FEMALE_NAMES_DE = {
    'anna', 'maria', 'monika', 'ursula', 'petra', 'sabine', 'andrea', 'claudia',
    'susanne', 'brigitte', 'gabriele', 'karin', 'ingrid', 'helga', 'renate',
    'christine', 'birgit', 'elisabeth', 'martina', 'barbara', 'heike', 'angela',
}

# Spanish names
MALE_NAMES_ES = {
    'jose', 'juan', 'carlos', 'miguel', 'antonio', 'francisco', 'pedro', 'luis',
    'jorge', 'rafael', 'manuel', 'fernando', 'ricardo', 'roberto', 'alejandro',
    'pablo', 'diego', 'sergio', 'alberto', 'javier', 'andres', 'raul', 'mario',
}

FEMALE_NAMES_ES = {
    'maria', 'carmen', 'ana', 'isabel', 'rosa', 'lucia', 'elena', 'dolores',
    'laura', 'pilar', 'marta', 'teresa', 'beatriz', 'cristina', 'patricia',
    'sara', 'silvia', 'monica', 'alicia', 'angela', 'paula', 'raquel', 'natalia',
}

# Combine all male names
ALL_MALE_NAMES = (
    MALE_NAMES_RU | MALE_NAMES_EN | MALE_NAMES_HE |
    MALE_NAMES_UK | MALE_NAMES_DE | MALE_NAMES_ES
)

# Combine all female names
ALL_FEMALE_NAMES = (
    FEMALE_NAMES_RU | FEMALE_NAMES_EN |
    FEMALE_NAMES_UK | FEMALE_NAMES_DE | FEMALE_NAMES_ES
)

# Names that are ambiguous (used for both genders)
AMBIGUOUS_NAMES = {'саша', 'женя', 'валя', 'alex', 'sam', 'jordan', 'taylor', 'casey', 'morgan'}


def normalize_name(name: str) -> str:
    """Normalize name for comparison"""
    if not name:
        return ''
    # Remove common prefixes/suffixes, lowercase, strip
    return name.lower().strip().replace('ё', 'е')


def detect_gender_from_name(name: str) -> Gender:
    """
    Detect gender from a first name.

    Args:
        name: The first name to analyze

    Returns:
        'male', 'female', or 'unknown'
    """
    if not name:
        return 'unknown'

    normalized = normalize_name(name)

    # Check ambiguous names first
    if normalized in AMBIGUOUS_NAMES:
        return 'unknown'

    # Check if in male names
    if normalized in ALL_MALE_NAMES:
        return 'male'

    # Check if in female names
    if normalized in ALL_FEMALE_NAMES:
        return 'female'

    # Heuristics based on name endings (Russian/Slavic names)
    # Female endings: -а, -я, -ия, -ья (but not -ша for diminutives like Саша)
    if len(normalized) > 2:
        # Strong female indicators
        if normalized.endswith(('ина', 'ена', 'ова', 'ева', 'ая', 'яя', 'ия', 'ья')):
            return 'female'

        # Strong male indicators for Russian/Slavic
        if normalized.endswith(('ий', 'ей', 'ой', 'ыч', 'ич')):
            return 'male'

    return 'unknown'


def detect_gender_from_last_name(last_name: str) -> Gender:
    """
    Detect gender from a last name (works for Slavic surnames).

    In Russian/Ukrainian, female surnames typically end in -а/-я:
    - Иванов (male) -> Иванова (female)
    - Петров (male) -> Петрова (female)

    Args:
        last_name: The last name to analyze

    Returns:
        'male', 'female', or 'unknown'
    """
    if not last_name:
        return 'unknown'

    normalized = normalize_name(last_name)

    if len(normalized) < 3:
        return 'unknown'

    # Check for female Slavic surname endings
    if normalized.endswith(('ова', 'ева', 'ёва', 'ина', 'ына', 'ая', 'яя', 'ська', 'цька')):
        return 'female'

    # Check for male Slavic surname endings
    if normalized.endswith(('ов', 'ев', 'ёв', 'ин', 'ын', 'ий', 'ой', 'ый', 'ський', 'цький')):
        return 'male'

    return 'unknown'


def detect_gender_from_username(username: str) -> Gender:
    """
    Try to detect gender from username by looking for embedded names.

    Args:
        username: Telegram username

    Returns:
        'male', 'female', or 'unknown'
    """
    if not username:
        return 'unknown'

    normalized = username.lower().strip()

    # Remove common username prefixes/suffixes
    # e.g., "marina_bakanova" -> try "marina"
    parts = normalized.replace('_', ' ').replace('-', ' ').replace('.', ' ').split()

    for part in parts:
        # Skip very short parts or numbers
        if len(part) < 3 or part.isdigit():
            continue

        # Try to detect gender from each part
        gender = detect_gender_from_name(part)
        if gender != 'unknown':
            return gender

    return 'unknown'


def detect_user_gender(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    username: Optional[str] = None
) -> Gender:
    """
    Detect user gender from available information.

    Priority:
    1. First name (most reliable)
    2. Last name (for Slavic surnames)
    3. Username (least reliable, only if name embedded)

    Args:
        first_name: User's first name from Telegram
        last_name: User's last name (if available)
        username: Telegram username

    Returns:
        'male', 'female', or 'unknown'
    """
    # Try first name first (most reliable)
    if first_name:
        gender = detect_gender_from_name(first_name)
        if gender != 'unknown':
            logger.debug(f"Gender detected from first_name '{first_name}': {gender}")
            return gender

    # Try last name (for Slavic names)
    if last_name:
        gender = detect_gender_from_last_name(last_name)
        if gender != 'unknown':
            logger.debug(f"Gender detected from last_name '{last_name}': {gender}")
            return gender

    # Try username as last resort
    if username:
        gender = detect_gender_from_username(username)
        if gender != 'unknown':
            logger.debug(f"Gender detected from username '{username}': {gender}")
            return gender

    logger.debug(f"Could not detect gender for: first_name={first_name}, last_name={last_name}, username={username}")
    return 'unknown'
